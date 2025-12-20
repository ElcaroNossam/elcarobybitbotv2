"""
HyperLiquid Exchange Implementation
"""
import logging
from typing import Dict, Any, Optional, List

from .base import (
    BaseExchange, Position, Order, Balance, OrderResult,
    OrderSide, OrderType, PositionSide,
)

from hyperliquid import HyperLiquidClient, HyperLiquidError


logger = logging.getLogger(__name__)


class HyperLiquidExchange(BaseExchange):
    def __init__(self, private_key: str, testnet: bool = False, vault_address: Optional[str] = None):
        self._client = HyperLiquidClient(private_key=private_key, testnet=testnet, vault_address=vault_address)
        self._testnet = testnet

    @property
    def name(self) -> str:
        return "HyperLiquid"

    async def initialize(self):
        await self._client.initialize()

    async def close(self):
        await self._client.close()

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def get_balance(self) -> Balance:
        bal = await self._client.get_balance()
        return Balance(
            total_equity=bal["account_value"],
            available_balance=bal["withdrawable"],
            margin_used=bal["total_margin_used"],
            unrealized_pnl=await self._client.get_unrealized_pnl(),
            currency="USDC",
        )

    async def get_positions(self) -> List[Position]:
        hl_positions = await self._client.get_all_positions()
        positions = []
        for pos in hl_positions:
            position = self._convert_position(pos)
            if position:
                positions.append(position)
        return positions

    async def get_position(self, symbol: str) -> Optional[Position]:
        coin = self.normalize_symbol(symbol)
        pos = await self._client.get_position(coin)
        if pos:
            return self._convert_position(pos)
        return None

    def _convert_position(self, hl_pos: Dict[str, Any]) -> Optional[Position]:
        size = float(hl_pos.get("szi", 0))
        if size == 0:
            return None
        leverage_info = hl_pos.get("leverage", {})
        leverage_value = leverage_info.get("value", 1) if isinstance(leverage_info, dict) else 1
        margin_mode = "cross" if leverage_info.get("type") == "cross" else "isolated"
        return Position(
            symbol=hl_pos.get("coin", ""),
            side=PositionSide.LONG if size > 0 else PositionSide.SHORT,
            size=abs(size),
            entry_price=float(hl_pos.get("entryPx", 0)),
            unrealized_pnl=float(hl_pos.get("unrealizedPnl", 0)),
            leverage=float(leverage_value),
            margin_mode=margin_mode,
            liquidation_price=float(hl_pos.get("liquidationPx")) if hl_pos.get("liquidationPx") else None,
            margin_used=float(hl_pos.get("marginUsed", 0)),
        )

    async def place_order(self, symbol: str, side: OrderSide, size: float, price: Optional[float] = None, order_type: OrderType = OrderType.MARKET, reduce_only: bool = False, client_order_id: Optional[str] = None) -> OrderResult:
        coin = self.normalize_symbol(symbol)
        is_buy = side == OrderSide.BUY
        try:
            if order_type == OrderType.MARKET or price is None:
                result = await self._client.market_open(coin=coin, is_buy=is_buy, sz=size, cloid=client_order_id)
            else:
                result = await self._client.order(coin=coin, is_buy=is_buy, sz=size, limit_px=price, reduce_only=reduce_only, cloid=client_order_id)

            status = result.get("status", "")
            if status == "ok":
                response = result.get("response", {})
                data = response.get("data", {})
                statuses = data.get("statuses", [])
                if statuses and "filled" in statuses[0]:
                    filled = statuses[0]["filled"]
                    return OrderResult(success=True, order_id=str(filled.get("oid", "")), filled_size=float(filled.get("totalSz", 0)), avg_price=float(filled.get("avgPx", 0)))
                elif statuses and "resting" in statuses[0]:
                    resting = statuses[0]["resting"]
                    return OrderResult(success=True, order_id=str(resting.get("oid", "")))
            return OrderResult(success=False, error=str(result))
        except HyperLiquidError as e:
            logger.error(f"Order failed: {e}")
            return OrderResult(success=False, error=str(e))

    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        coin = self.normalize_symbol(symbol)
        try:
            result = await self._client.cancel(coin, int(order_id))
            return result.get("status") == "ok"
        except (HyperLiquidError, ValueError) as e:
            logger.error(f"Cancel failed: {e}")
            return False

    async def cancel_all_orders(self, symbol: Optional[str] = None) -> int:
        try:
            results = await self._client.cancel_all()
            return len([r for r in results if "result" in r])
        except HyperLiquidError as e:
            logger.error(f"Cancel all failed: {e}")
            return 0

    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        hl_orders = await self._client.open_orders()
        orders = []
        for o in hl_orders:
            if symbol and self.normalize_symbol(symbol) != o.get("coin"):
                continue
            orders.append(Order(
                order_id=str(o.get("oid", "")),
                symbol=o.get("coin", ""),
                side=OrderSide.BUY if o.get("side") == "B" else OrderSide.SELL,
                order_type=OrderType.LIMIT,
                size=float(o.get("sz", 0)),
                price=float(o.get("limitPx", 0)),
                filled_size=float(o.get("sz", 0)) - float(o.get("origSz", o.get("sz", 0))),
                status="open",
                reduce_only=o.get("reduceOnly", False),
                client_order_id=o.get("cloid"),
                created_at=o.get("timestamp"),
            ))
        return orders

    async def set_leverage(self, symbol: str, leverage: int) -> bool:
        coin = self.normalize_symbol(symbol)
        try:
            result = await self._client.update_leverage(coin, leverage, is_cross=True)
            return result.get("status") == "ok"
        except HyperLiquidError as e:
            logger.error(f"Set leverage failed: {e}")
            return False

    async def set_take_profit(self, symbol: str, price: float, size: Optional[float] = None) -> OrderResult:
        coin = self.normalize_symbol(symbol)
        try:
            results = await self._client.set_tp_sl(coin=coin, tp_price=price, sz=size)
            for r in results:
                if r.get("type") == "tp":
                    result = r.get("result", {})
                    if result.get("status") == "ok":
                        return OrderResult(success=True)
                    return OrderResult(success=False, error=str(result))
            return OrderResult(success=False, error="TP not set")
        except HyperLiquidError as e:
            logger.error(f"Set TP failed: {e}")
            return OrderResult(success=False, error=str(e))

    async def set_stop_loss(self, symbol: str, price: float, size: Optional[float] = None) -> OrderResult:
        coin = self.normalize_symbol(symbol)
        try:
            results = await self._client.set_tp_sl(coin=coin, sl_price=price, sz=size)
            for r in results:
                if r.get("type") == "sl":
                    result = r.get("result", {})
                    if result.get("status") == "ok":
                        return OrderResult(success=True)
                    return OrderResult(success=False, error=str(result))
            return OrderResult(success=False, error="SL not set")
        except HyperLiquidError as e:
            logger.error(f"Set SL failed: {e}")
            return OrderResult(success=False, error=str(e))

    async def close_position(self, symbol: str, size: Optional[float] = None) -> OrderResult:
        coin = self.normalize_symbol(symbol)
        try:
            result = await self._client.market_close(coin=coin, sz=size)
            if result.get("status") == "ok":
                return OrderResult(success=True)
            return OrderResult(success=False, error=str(result))
        except HyperLiquidError as e:
            logger.error(f"Close position failed: {e}")
            return OrderResult(success=False, error=str(e))

    async def get_price(self, symbol: str) -> Optional[float]:
        coin = self.normalize_symbol(symbol)
        return await self._client.get_mid_price(coin)

    async def get_orderbook(self, symbol: str, depth: int = 10) -> Dict[str, Any]:
        coin = self.normalize_symbol(symbol)
        return await self._client.l2_snapshot(coin)

    def normalize_symbol(self, symbol: str) -> str:
        s = symbol.upper()
        for suffix in ["USDT", "USDC", "PERP", "-PERP", "_PERP"]:
            s = s.replace(suffix, "")
        return s
