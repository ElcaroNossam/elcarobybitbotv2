"""
Unified Trading Service
"""
import logging
from typing import Dict, Any, Optional, List, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum

from hl_adapter import HLAdapter, create_hl_adapter


logger = logging.getLogger(__name__)


class ExchangeType(Enum):
    BYBIT = "bybit"
    HYPERLIQUID = "hyperliquid"


@dataclass
class TradeResult:
    success: bool
    order_id: Optional[str] = None
    message: str = ""
    exchange: str = ""
    symbol: str = ""
    side: str = ""
    size: float = 0
    price: Optional[float] = None
    error: Optional[str] = None


class TradingService:
    def __init__(self, exchange_type: ExchangeType = ExchangeType.HYPERLIQUID, bybit_request_fn: Optional[Callable[..., Awaitable[Dict]]] = None):
        self._exchange_type = exchange_type
        self._bybit_request = bybit_request_fn
        self._hl_adapter: Optional[HLAdapter] = None
        self._user_id: Optional[int] = None
        self._initialized = False

    @property
    def exchange_name(self) -> str:
        return self._exchange_type.value

    @property
    def is_hyperliquid(self) -> bool:
        return self._exchange_type == ExchangeType.HYPERLIQUID

    async def initialize(self, user_id: int, private_key: Optional[str] = None, testnet: bool = False, vault_address: Optional[str] = None):
        self._user_id = user_id
        if self._exchange_type == ExchangeType.HYPERLIQUID:
            if not private_key:
                raise ValueError("Private key required for HyperLiquid")
            self._hl_adapter = await create_hl_adapter(private_key=private_key, testnet=testnet, vault_address=vault_address)
        self._initialized = True

    async def close(self):
        if self._hl_adapter:
            await self._hl_adapter.close()
            self._hl_adapter = None
        self._initialized = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def get_balance(self) -> Dict[str, Any]:
        self._check_initialized()
        if self.is_hyperliquid:
            return await self._hl_adapter.fetch_balance()
        else:
            return await self._bybit_request(self._user_id, "GET", "/v5/account/wallet-balance", params={"accountType": "UNIFIED"})

    async def get_positions(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        self._check_initialized()
        if self.is_hyperliquid:
            return await self._hl_adapter.fetch_positions(symbol)
        else:
            params = {"category": "linear", "settleCoin": "USDT"}
            if symbol:
                params["symbol"] = symbol
            return await self._bybit_request(self._user_id, "GET", "/v5/position/list", params=params)

    async def get_open_orders(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        self._check_initialized()
        if self.is_hyperliquid:
            return await self._hl_adapter.fetch_orders(symbol)
        else:
            params = {"category": "linear"}
            if symbol:
                params["symbol"] = symbol
            return await self._bybit_request(self._user_id, "GET", "/v5/order/realtime", params=params)

    async def open_position(self, symbol: str, side: str, size: float, leverage: int = 10, price: Optional[float] = None, take_profit: Optional[float] = None, stop_loss: Optional[float] = None) -> TradeResult:
        self._check_initialized()
        try:
            await self.set_leverage(symbol, leverage)
            if self.is_hyperliquid:
                result = await self._hl_adapter.place_order(symbol=symbol, side=side, qty=size, price=price, order_type="Limit" if price else "Market", take_profit=take_profit, stop_loss=stop_loss)
                if result.get("retCode") == 0:
                    return TradeResult(success=True, order_id=result.get("result", {}).get("orderId"), message="Order placed successfully", exchange="hyperliquid", symbol=symbol, side=side, size=size)
                else:
                    return TradeResult(success=False, error=result.get("retMsg"), exchange="hyperliquid", symbol=symbol, side=side)
            else:
                body = {"category": "linear", "symbol": symbol, "side": side, "orderType": "Limit" if price else "Market", "qty": str(size)}
                if price:
                    body["price"] = str(price)
                if take_profit:
                    body["takeProfit"] = str(take_profit)
                if stop_loss:
                    body["stopLoss"] = str(stop_loss)
                result = await self._bybit_request(self._user_id, "POST", "/v5/order/create", body=body)
                if result.get("retCode") == 0:
                    return TradeResult(success=True, order_id=result.get("result", {}).get("orderId"), message="Order placed successfully", exchange="bybit", symbol=symbol, side=side, size=size)
                else:
                    return TradeResult(success=False, error=result.get("retMsg"), exchange="bybit", symbol=symbol, side=side)
        except Exception as e:
            logger.error(f"open_position error: {e}")
            return TradeResult(success=False, error=str(e), exchange=self.exchange_name, symbol=symbol, side=side)

    async def close_position(self, symbol: str, size: Optional[float] = None) -> TradeResult:
        self._check_initialized()
        try:
            if self.is_hyperliquid:
                result = await self._hl_adapter.close_position(symbol, size)
                return TradeResult(success=result.get("retCode") == 0, message=result.get("retMsg", ""), error=result.get("retMsg") if result.get("retCode") != 0 else None, exchange="hyperliquid", symbol=symbol)
            else:
                positions = await self.get_positions(symbol)
                pos_list = positions.get("result", {}).get("list", [])
                if not pos_list:
                    return TradeResult(success=False, error="No position found", exchange="bybit", symbol=symbol)
                pos = pos_list[0]
                pos_side = pos.get("side")
                pos_size = float(pos.get("size", 0))
                close_side = "Sell" if pos_side == "Buy" else "Buy"
                close_size = size or pos_size
                body = {"category": "linear", "symbol": symbol, "side": close_side, "orderType": "Market", "qty": str(close_size), "reduceOnly": True}
                result = await self._bybit_request(self._user_id, "POST", "/v5/order/create", body=body)
                return TradeResult(success=result.get("retCode") == 0, order_id=result.get("result", {}).get("orderId"), message=result.get("retMsg", ""), error=result.get("retMsg") if result.get("retCode") != 0 else None, exchange="bybit", symbol=symbol)
        except Exception as e:
            logger.error(f"close_position error: {e}")
            return TradeResult(success=False, error=str(e), exchange=self.exchange_name, symbol=symbol)

    async def set_leverage(self, symbol: str, leverage: int) -> bool:
        self._check_initialized()
        try:
            if self.is_hyperliquid:
                result = await self._hl_adapter.set_leverage(symbol, leverage)
                return result.get("retCode") == 0
            else:
                result = await self._bybit_request(self._user_id, "POST", "/v5/position/set-leverage", body={"category": "linear", "symbol": symbol, "buyLeverage": str(leverage), "sellLeverage": str(leverage)})
                return result.get("retCode") in [0, 110043]
        except Exception as e:
            logger.error(f"set_leverage error: {e}")
            return False

    async def set_stop_loss(self, symbol: str, price: float, size: Optional[float] = None) -> TradeResult:
        self._check_initialized()
        try:
            if self.is_hyperliquid:
                result = await self._hl_adapter.set_stop_loss(symbol, price, size)
                return TradeResult(success=result.get("retCode") == 0, message=result.get("retMsg", ""), error=result.get("retMsg") if result.get("retCode") != 0 else None, exchange="hyperliquid", symbol=symbol)
            else:
                result = await self._bybit_request(self._user_id, "POST", "/v5/position/trading-stop", body={"category": "linear", "symbol": symbol, "stopLoss": str(price)})
                return TradeResult(success=result.get("retCode") == 0, message=result.get("retMsg", ""), error=result.get("retMsg") if result.get("retCode") != 0 else None, exchange="bybit", symbol=symbol)
        except Exception as e:
            logger.error(f"set_stop_loss error: {e}")
            return TradeResult(success=False, error=str(e), exchange=self.exchange_name, symbol=symbol)

    async def set_take_profit(self, symbol: str, price: float, size: Optional[float] = None) -> TradeResult:
        self._check_initialized()
        try:
            if self.is_hyperliquid:
                result = await self._hl_adapter.set_take_profit(symbol, price, size)
                return TradeResult(success=result.get("retCode") == 0, message=result.get("retMsg", ""), error=result.get("retMsg") if result.get("retCode") != 0 else None, exchange="hyperliquid", symbol=symbol)
            else:
                result = await self._bybit_request(self._user_id, "POST", "/v5/position/trading-stop", body={"category": "linear", "symbol": symbol, "takeProfit": str(price)})
                return TradeResult(success=result.get("retCode") == 0, message=result.get("retMsg", ""), error=result.get("retMsg") if result.get("retCode") != 0 else None, exchange="bybit", symbol=symbol)
        except Exception as e:
            logger.error(f"set_take_profit error: {e}")
            return TradeResult(success=False, error=str(e), exchange=self.exchange_name, symbol=symbol)

    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        self._check_initialized()
        try:
            if self.is_hyperliquid:
                result = await self._hl_adapter.cancel_order(symbol, order_id)
                return result.get("retCode") == 0
            else:
                result = await self._bybit_request(self._user_id, "POST", "/v5/order/cancel", body={"category": "linear", "symbol": symbol, "orderId": order_id})
                return result.get("retCode") == 0
        except Exception as e:
            logger.error(f"cancel_order error: {e}")
            return False

    async def cancel_all_orders(self, symbol: Optional[str] = None) -> int:
        self._check_initialized()
        try:
            if self.is_hyperliquid:
                result = await self._hl_adapter.cancel_all_orders(symbol)
                return result.get("result", {}).get("count", 0)
            else:
                body = {"category": "linear"}
                if symbol:
                    body["symbol"] = symbol
                result = await self._bybit_request(self._user_id, "POST", "/v5/order/cancel-all", body=body)
                return len(result.get("result", {}).get("list", []))
        except Exception as e:
            logger.error(f"cancel_all_orders error: {e}")
            return 0

    async def get_price(self, symbol: str) -> Optional[float]:
        self._check_initialized()
        try:
            if self.is_hyperliquid:
                return await self._hl_adapter.get_price(symbol)
            else:
                result = await self._bybit_request(self._user_id, "GET", "/v5/market/tickers", params={"category": "linear", "symbol": symbol})
                tickers = result.get("result", {}).get("list", [])
                if tickers:
                    return float(tickers[0].get("lastPrice", 0))
                return None
        except Exception as e:
            logger.error(f"get_price error: {e}")
            return None

    def _check_initialized(self):
        if not self._initialized:
            raise RuntimeError("Trading service not initialized")

    def normalize_symbol(self, symbol: str) -> str:
        if self.is_hyperliquid:
            s = symbol.upper()
            for suffix in ["USDT", "USDC", "PERP", "-PERP", "_PERP"]:
                s = s.replace(suffix, "")
            return s
        else:
            s = symbol.upper()
            for suffix in ["USDC", "PERP", "-PERP", "_PERP"]:
                s = s.replace(suffix, "")
            if not s.endswith("USDT"):
                s = s + "USDT"
            return s


async def create_trading_service(exchange_type: ExchangeType, user_id: int, private_key: Optional[str] = None, testnet: bool = False, vault_address: Optional[str] = None, bybit_request_fn: Optional[Callable] = None) -> TradingService:
    service = TradingService(exchange_type=exchange_type, bybit_request_fn=bybit_request_fn)
    await service.initialize(user_id=user_id, private_key=private_key, testnet=testnet, vault_address=vault_address)
    return service
