"""
HyperLiquid Adapter for Bot Compatibility
"""
import logging
from typing import Dict, Any, Optional, List

from hyperliquid import HyperLiquidClient, HyperLiquidError, coin_to_asset_id


logger = logging.getLogger(__name__)


class HLAdapter:
    def __init__(self, private_key: str, testnet: bool = False, vault_address: Optional[str] = None):
        self._client = HyperLiquidClient(private_key=private_key, testnet=testnet, vault_address=vault_address)
        self._initialized = False

    @property
    def address(self) -> str:
        return self._client.address

    @property
    def is_testnet(self) -> bool:
        return self._client.is_testnet

    async def initialize(self):
        if not self._initialized:
            await self._client.initialize()
            self._initialized = True

    async def close(self):
        if self._initialized:
            await self._client.close()
            self._initialized = False

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def fetch_positions(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        await self.initialize()
        try:
            positions = await self._client.get_all_positions()
            result_list = []
            for pos in positions:
                coin = pos.get("coin", "")
                if symbol and self._normalize_symbol(symbol) != coin:
                    continue
                size = float(pos.get("szi", 0))
                if size == 0:
                    continue
                leverage_info = pos.get("leverage", {})
                leverage = leverage_info.get("value", 1) if isinstance(leverage_info, dict) else 1
                result_list.append({
                    "symbol": f"{coin}USDC",
                    "side": "Buy" if size > 0 else "Sell",
                    "size": str(abs(size)),
                    "positionValue": str(pos.get("positionValue", 0)),
                    "entryPrice": str(pos.get("entryPx", 0)),
                    "markPrice": str(pos.get("entryPx", 0)),
                    "liqPrice": str(pos.get("liquidationPx", 0)) if pos.get("liquidationPx") else "0",
                    "leverage": str(leverage),
                    "unrealisedPnl": str(pos.get("unrealizedPnl", 0)),
                    "cumRealisedPnl": "0",
                    "positionMM": str(pos.get("marginUsed", 0)),
                    "positionIM": str(pos.get("marginUsed", 0)),
                    "takeProfit": "",
                    "stopLoss": "",
                    "tradeMode": 0 if leverage_info.get("type") == "cross" else 1,
                    "_hl_coin": coin,
                    "_hl_raw": pos,
                })
            return {"retCode": 0, "retMsg": "OK", "result": {"list": result_list, "category": "linear"}}
        except HyperLiquidError as e:
            logger.error(f"fetch_positions error: {e}")
            return {"retCode": 1, "retMsg": str(e), "result": {"list": []}}

    async def fetch_orders(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        await self.initialize()
        try:
            orders = await self._client.open_orders()
            result_list = []
            for order in orders:
                coin = order.get("coin", "")
                if symbol and self._normalize_symbol(symbol) != coin:
                    continue
                result_list.append({
                    "orderId": str(order.get("oid", "")),
                    "symbol": f"{coin}USDC",
                    "side": "Buy" if order.get("side") == "B" else "Sell",
                    "orderType": "Limit",
                    "price": str(order.get("limitPx", 0)),
                    "qty": str(order.get("sz", 0)),
                    "cumExecQty": "0",
                    "orderStatus": "New",
                    "reduceOnly": order.get("reduceOnly", False),
                    "createdTime": str(order.get("timestamp", 0)),
                    "updatedTime": str(order.get("timestamp", 0)),
                    "_hl_coin": coin,
                    "_hl_cloid": order.get("cloid"),
                })
            return {"retCode": 0, "retMsg": "OK", "result": {"list": result_list, "category": "linear"}}
        except HyperLiquidError as e:
            logger.error(f"fetch_orders error: {e}")
            return {"retCode": 1, "retMsg": str(e), "result": {"list": []}}

    async def fetch_balance(self) -> Dict[str, Any]:
        await self.initialize()
        try:
            balance = await self._client.get_balance()
            pnl = await self._client.get_unrealized_pnl()
            return {
                "retCode": 0, "retMsg": "OK",
                "result": {"list": [{
                    "accountType": "UNIFIED",
                    "totalEquity": str(balance["account_value"]),
                    "totalWalletBalance": str(balance["account_value"]),
                    "totalAvailableBalance": str(balance["withdrawable"]),
                    "totalMarginBalance": str(balance["account_value"]),
                    "totalPerpUPL": str(pnl),
                    "coin": [{"coin": "USDC", "equity": str(balance["account_value"]), "walletBalance": str(balance["account_value"]), "availableToWithdraw": str(balance["withdrawable"]), "unrealisedPnl": str(pnl)}],
                }]}
            }
        except HyperLiquidError as e:
            logger.error(f"fetch_balance error: {e}")
            return {"retCode": 1, "retMsg": str(e), "result": {"list": []}}

    async def get_balance(self) -> Dict[str, Any]:
        """Simplified balance method for UI"""
        await self.initialize()
        try:
            balance = await self._client.get_balance()
            pnl = await self._client.get_unrealized_pnl()
            return {
                "success": True,
                "data": {
                    "equity": balance.get("account_value", 0),
                    "available": balance.get("withdrawable", 0),
                    "margin_used": balance.get("margin_used", 0),
                    "unrealized_pnl": pnl
                }
            }
        except Exception as e:
            logger.error(f"get_balance error: {e}")
            return {"success": False, "error": str(e)}

    async def fetch_open_orders(self) -> Dict[str, Any]:
        """Simplified open orders for UI"""
        await self.initialize()
        try:
            orders = await self._client.open_orders()
            result_list = []
            for order in orders:
                coin = order.get("coin", "")
                result_list.append({
                    "symbol": f"{coin}USDC",
                    "side": "Buy" if order.get("side") == "B" else "Sell",
                    "size": float(order.get("sz", 0)),
                    "price": float(order.get("limitPx", 0)),
                    "order_type": "Limit",
                    "order_id": str(order.get("oid", "")),
                })
            return {"success": True, "data": result_list}
        except Exception as e:
            logger.error(f"fetch_open_orders error: {e}")
            return {"success": False, "error": str(e)}

    async def fetch_trade_history(self, limit: int = 10) -> Dict[str, Any]:
        """Fetch trade history for UI"""
        await self.initialize()
        try:
            # HyperLiquid API for user fills
            fills = await self._client.user_fills()
            result_list = []
            for fill in fills[:limit]:
                result_list.append({
                    "symbol": f"{fill.get('coin', '')}USDC",
                    "side": "Buy" if fill.get("side") == "B" else "Sell",
                    "size": float(fill.get("sz", 0)),
                    "price": float(fill.get("px", 0)),
                    "pnl": float(fill.get("closedPnl", 0)),
                    "time": fill.get("time", 0),
                })
            return {"success": True, "data": result_list}
        except Exception as e:
            logger.error(f"fetch_trade_history error: {e}")
            return {"success": False, "error": str(e)}

    async def place_order(self, symbol: str, side: str, qty: float, price: Optional[float] = None, order_type: str = "Market", reduce_only: bool = False, take_profit: Optional[float] = None, stop_loss: Optional[float] = None) -> Dict[str, Any]:
        await self.initialize()
        coin = self._normalize_symbol(symbol)
        is_buy = side.lower() == "buy"
        try:
            if order_type.lower() == "market" or price is None:
                result = await self._client.market_open(coin=coin, is_buy=is_buy, sz=qty)
            else:
                result = await self._client.order(coin=coin, is_buy=is_buy, sz=qty, limit_px=price, reduce_only=reduce_only)

            order_id = None
            if result.get("status") == "ok":
                response = result.get("response", {})
                data = response.get("data", {})
                statuses = data.get("statuses", [])
                if statuses:
                    if "filled" in statuses[0]:
                        order_id = str(statuses[0]["filled"].get("oid", ""))
                    elif "resting" in statuses[0]:
                        order_id = str(statuses[0]["resting"].get("oid", ""))

            if order_id and (take_profit or stop_loss):
                try:
                    await self._client.set_tp_sl(coin=coin, tp_price=take_profit, sl_price=stop_loss)
                except Exception as e:
                    logger.warning(f"Failed to set TP/SL: {e}")

            return {"retCode": 0 if result.get("status") == "ok" else 1, "retMsg": "OK" if result.get("status") == "ok" else str(result), "result": {"orderId": order_id or "", "orderLinkId": ""}}
        except HyperLiquidError as e:
            logger.error(f"place_order error: {e}")
            return {"retCode": 1, "retMsg": str(e), "result": {}}

    async def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        await self.initialize()
        coin = self._normalize_symbol(symbol)
        try:
            result = await self._client.cancel(coin, int(order_id))
            return {"retCode": 0 if result.get("status") == "ok" else 1, "retMsg": "OK" if result.get("status") == "ok" else str(result), "result": {}}
        except (HyperLiquidError, ValueError) as e:
            logger.error(f"cancel_order error: {e}")
            return {"retCode": 1, "retMsg": str(e), "result": {}}

    async def cancel_all_orders(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        await self.initialize()
        try:
            results = await self._client.cancel_all()
            cancelled = len([r for r in results if "result" in r])
            return {"retCode": 0, "retMsg": f"Cancelled {cancelled} orders", "result": {"count": cancelled}}
        except HyperLiquidError as e:
            logger.error(f"cancel_all_orders error: {e}")
            return {"retCode": 1, "retMsg": str(e), "result": {}}

    async def set_leverage(self, symbol: str, leverage: int) -> Dict[str, Any]:
        await self.initialize()
        coin = self._normalize_symbol(symbol)
        try:
            result = await self._client.update_leverage(coin=coin, leverage=leverage, is_cross=True)
            return {"retCode": 0 if result.get("status") == "ok" else 1, "retMsg": "OK" if result.get("status") == "ok" else str(result), "result": {}}
        except HyperLiquidError as e:
            logger.error(f"set_leverage error: {e}")
            return {"retCode": 1, "retMsg": str(e), "result": {}}

    async def set_stop_loss(self, symbol: str, stop_loss_price: float, qty: Optional[float] = None) -> Dict[str, Any]:
        await self.initialize()
        coin = self._normalize_symbol(symbol)
        try:
            results = await self._client.set_tp_sl(coin=coin, sl_price=stop_loss_price, sz=qty)
            for r in results:
                if r.get("type") == "sl":
                    result = r.get("result", {})
                    return {"retCode": 0 if result.get("status") == "ok" else 1, "retMsg": "OK" if result.get("status") == "ok" else str(result), "result": {}}
            return {"retCode": 1, "retMsg": "SL not set", "result": {}}
        except HyperLiquidError as e:
            logger.error(f"set_stop_loss error: {e}")
            return {"retCode": 1, "retMsg": str(e), "result": {}}

    async def set_take_profit(self, symbol: str, take_profit_price: float, qty: Optional[float] = None) -> Dict[str, Any]:
        await self.initialize()
        coin = self._normalize_symbol(symbol)
        try:
            results = await self._client.set_tp_sl(coin=coin, tp_price=take_profit_price, sz=qty)
            for r in results:
                if r.get("type") == "tp":
                    result = r.get("result", {})
                    return {"retCode": 0 if result.get("status") == "ok" else 1, "retMsg": "OK" if result.get("status") == "ok" else str(result), "result": {}}
            return {"retCode": 1, "retMsg": "TP not set", "result": {}}
        except HyperLiquidError as e:
            logger.error(f"set_take_profit error: {e}")
            return {"retCode": 1, "retMsg": str(e), "result": {}}

    async def close_position(self, symbol: str, qty: Optional[float] = None) -> Dict[str, Any]:
        await self.initialize()
        coin = self._normalize_symbol(symbol)
        try:
            result = await self._client.market_close(coin=coin, sz=qty)
            return {"retCode": 0 if result.get("status") == "ok" else 1, "retMsg": "OK" if result.get("status") == "ok" else str(result), "result": {}}
        except HyperLiquidError as e:
            logger.error(f"close_position error: {e}")
            return {"retCode": 1, "retMsg": str(e), "result": {}}

    async def get_price(self, symbol: str) -> Optional[float]:
        await self.initialize()
        coin = self._normalize_symbol(symbol)
        return await self._client.get_mid_price(coin)

    async def get_all_prices(self) -> Dict[str, float]:
        await self.initialize()
        return await self._client.get_all_mids()

    def _normalize_symbol(self, symbol: str) -> str:
        s = symbol.upper()
        for suffix in ["USDT", "USDC", "PERP", "-PERP", "_PERP"]:
            s = s.replace(suffix, "")
        return s

    @staticmethod
    def is_supported_symbol(symbol: str) -> bool:
        coin = symbol.upper()
        for suffix in ["USDT", "USDC", "PERP", "-PERP", "_PERP"]:
            coin = coin.replace(suffix, "")
        return coin_to_asset_id(coin) is not None


async def create_hl_adapter(private_key: str, testnet: bool = False, vault_address: Optional[str] = None) -> HLAdapter:
    adapter = HLAdapter(private_key=private_key, testnet=testnet, vault_address=vault_address)
    await adapter.initialize()
    return adapter
