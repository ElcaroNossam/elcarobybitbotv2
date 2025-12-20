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
    
    @property
    def address(self) -> str:
        return self._address
    
    @property
    def is_testnet(self) -> bool:
        return self._testnet
    
    async def initialize(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._own_session = True
    
    async def close(self):
        if self._own_session and self._session and not self._session.closed:
            await self._session.close()
    
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def _request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        if self._session is None or self._session.closed:
            await self.initialize()
        
        url = f"{self._base_url}{endpoint}"
        
        try:
            async with self._session.request(method, url, json=data, params=params, headers={"Content-Type": "application/json"}) as response:
                text = await response.text()
                if response.status >= 400:
                    logger.error(f"HyperLiquid API error: {response.status} - {text}")
                    raise HyperLiquidError(f"API error: {text}", status_code=response.status, response={"error": text})
                if not text:
                    return {}
                return json.loads(text)
        except aiohttp.ClientError as e:
            logger.error(f"HyperLiquid request failed: {e}")
            raise HyperLiquidError(f"Request failed: {e}")
    
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
        return {k: float(v) for k, v in result.items()}
    
    async def get_mid_price(self, coin: str) -> Optional[float]:
        mids = await self.get_all_mids()
        return mids.get(coin)
    
    async def user_state(self, address: Optional[str] = None) -> Dict[str, Any]:
        addr = address or self._address
        return await self._info_request("clearinghouseState", user=addr)
    
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
        limit_px = round(limit_px, 5)
        
        return await self.order(coin=coin, is_buy=is_buy, sz=sz, limit_px=limit_px, reduce_only=False, order_type={"limit": {"tif": "Ioc"}}, cloid=cloid)
    
    async def market_close(self, coin: str, sz: Optional[float] = None, slippage: float = 0.01, cloid: Optional[str] = None) -> Dict[str, Any]:
        state = await self.user_state()
        position = None
        
        for pos in state.get("assetPositions", []):
            pos_info = pos.get("position", {})
            if pos_info.get("coin") == coin:
                position = pos_info
                break
        
        if position is None:
            raise HyperLiquidError(f"No position found for {coin}")
        
        position_size = float(position.get("szi", 0))
        if position_size == 0:
            raise HyperLiquidError(f"Position size is 0 for {coin}")
        
        close_size = sz if sz is not None else abs(position_size)
        is_buy = position_size < 0
        
        mid_price = await self.get_mid_price(coin)
        if mid_price is None:
            raise HyperLiquidError(f"Cannot get price for {coin}")
        
        limit_px = mid_price * (1 + slippage) if is_buy else mid_price * (1 - slippage)
        limit_px = round(limit_px, 5)
        
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
    
    async def set_tp_sl(self, coin: str, tp_price: Optional[float] = None, sl_price: Optional[float] = None, sz: Optional[float] = None) -> List[Dict[str, Any]]:
        state = await self.user_state()
        position = None
        
        for pos in state.get("assetPositions", []):
            pos_info = pos.get("position", {})
            if pos_info.get("coin") == coin:
                position = pos_info
                break
        
        if position is None:
            raise HyperLiquidError(f"No position found for {coin}")
        
        position_size = float(position.get("szi", 0))
        if position_size == 0:
            raise HyperLiquidError(f"Position size is 0 for {coin}")
        
        order_size = sz if sz is not None else abs(position_size)
        is_long = position_size > 0
        results = []
        
        if tp_price is not None:
            tp_result = await self.order(coin=coin, is_buy=not is_long, sz=order_size, limit_px=tp_price, reduce_only=True, order_type={"trigger": {"isMarket": True, "triggerPx": tp_price, "tpsl": "tp"}})
            results.append({"type": "tp", "result": tp_result})
        
        if sl_price is not None:
            sl_result = await self.order(coin=coin, is_buy=not is_long, sz=order_size, limit_px=sl_price, reduce_only=True, order_type={"trigger": {"isMarket": True, "triggerPx": sl_price, "tpsl": "sl"}})
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
            if float(pos_info.get("szi", 0)) != 0:
                positions.append(pos_info)
        return positions
    
    async def get_balance(self) -> Dict[str, float]:
        state = await self.user_state()
        margin = state.get("marginSummary", {})
        return {
            "account_value": float(margin.get("accountValue", 0)),
            "total_margin_used": float(margin.get("totalMarginUsed", 0)),
            "total_ntl_pos": float(margin.get("totalNtlPos", 0)),
            "withdrawable": float(state.get("withdrawable", 0)),
        }
    
    async def get_unrealized_pnl(self) -> float:
        positions = await self.get_all_positions()
        total_pnl = 0.0
        for pos in positions:
            pnl = float(pos.get("unrealizedPnl", 0))
            total_pnl += pnl
        return total_pnl
