"""
HyperLiquid Adapter for Bot Compatibility
"""
import logging
from typing import Dict, Any, Optional, List

from hyperliquid import HyperLiquidClient, HyperLiquidError, coin_to_asset_id
from models import Position, Order, Balance, OrderResult, OrderSide, PositionSide

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

    # ==================== NEW ADVANCED FEATURES ====================

    async def get_candles(
        self,
        symbol: str,
        interval: str = "1h",
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get OHLCV candle data.
        Intervals: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 8h, 12h, 1d, 3d, 1w, 1M
        """
        await self.initialize()
        coin = self._normalize_symbol(symbol)
        try:
            candles = await self._client.get_candles(coin, interval, start_time, end_time)
            result_list = []
            for c in candles:
                result_list.append({
                    "timestamp": c.get("t", 0),
                    "open": float(c.get("o", 0)),
                    "high": float(c.get("h", 0)),
                    "low": float(c.get("l", 0)),
                    "close": float(c.get("c", 0)),
                    "volume": float(c.get("v", 0)),
                    "trades": c.get("n", 0),
                })
            return {"success": True, "data": result_list}
        except Exception as e:
            logger.error(f"get_candles error: {e}")
            return {"success": False, "error": str(e)}

    async def get_historical_orders(self) -> Dict[str, Any]:
        """Get historical orders"""
        await self.initialize()
        try:
            orders = await self._client.get_historical_orders()
            result_list = []
            for o in orders:
                order = o.get("order", {})
                result_list.append({
                    "orderId": str(order.get("oid", "")),
                    "symbol": f"{order.get('coin', '')}USDC",
                    "side": "Buy" if order.get("side") == "B" else "Sell",
                    "orderType": order.get("orderType", ""),
                    "price": order.get("limitPx", "0"),
                    "size": order.get("origSz", "0"),
                    "status": o.get("status", ""),
                    "reduceOnly": order.get("reduceOnly", False),
                    "timestamp": order.get("timestamp", 0),
                })
            return {"success": True, "data": result_list}
        except Exception as e:
            logger.error(f"get_historical_orders error: {e}")
            return {"success": False, "error": str(e)}

    async def get_order_status(self, order_id: int = None, cloid: str = None) -> Dict[str, Any]:
        """Get status of a specific order"""
        await self.initialize()
        try:
            result = await self._client.get_order_status(oid=order_id, cloid=cloid)
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"get_order_status error: {e}")
            return {"success": False, "error": str(e)}

    async def get_rate_limits(self) -> Dict[str, Any]:
        """Get user rate limits"""
        await self.initialize()
        try:
            limits = await self._client.get_rate_limits()
            return {"success": True, "data": limits}
        except Exception as e:
            logger.error(f"get_rate_limits error: {e}")
            return {"success": False, "error": str(e)}

    async def get_user_fees(self) -> Dict[str, Any]:
        """Get user fee schedule"""
        await self.initialize()
        try:
            fees = await self._client.get_user_fees()
            return {"success": True, "data": fees}
        except Exception as e:
            logger.error(f"get_user_fees error: {e}")
            return {"success": False, "error": str(e)}

    async def get_portfolio(self) -> Dict[str, Any]:
        """Get portfolio with PnL history"""
        await self.initialize()
        try:
            portfolio = await self._client.get_portfolio()
            return {"success": True, "data": portfolio}
        except Exception as e:
            logger.error(f"get_portfolio error: {e}")
            return {"success": False, "error": str(e)}

    async def get_referral_info(self) -> Dict[str, Any]:
        """Get referral information"""
        await self.initialize()
        try:
            info = await self._client.get_referral_info()
            return {"success": True, "data": info}
        except Exception as e:
            logger.error(f"get_referral_info error: {e}")
            return {"success": False, "error": str(e)}

    async def get_subaccounts(self) -> Dict[str, Any]:
        """Get list of subaccounts"""
        await self.initialize()
        try:
            accounts = await self._client.get_subaccounts()
            return {"success": True, "data": accounts if accounts else []}
        except Exception as e:
            logger.error(f"get_subaccounts error: {e}")
            return {"success": False, "error": str(e)}

    async def get_meta(self) -> Dict[str, Any]:
        """Get exchange metadata (all coins info)"""
        await self.initialize()
        try:
            meta = await self._client.meta()
            return meta
        except Exception as e:
            logger.error(f"get_meta error: {e}")
            return {}

    async def get_all_coins_info(self) -> Dict[str, Any]:
        """Get detailed info for all coins"""
        await self.initialize()
        try:
            coins = await self._client.get_all_coins_info()
            return {"success": True, "data": coins}
        except Exception as e:
            logger.error(f"get_all_coins_info error: {e}")
            return {"success": False, "error": str(e)}

    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker info for a symbol"""
        await self.initialize()
        coin = self._normalize_symbol(symbol)
        try:
            ticker = await self._client.get_ticker(coin)
            return ticker if ticker else {}
        except Exception as e:
            logger.error(f"get_ticker error: {e}")
            return {}

    async def get_orderbook(self, symbol: str, depth: int = 20) -> Dict[str, Any]:
        """Get L2 orderbook"""
        await self.initialize()
        coin = self._normalize_symbol(symbol)
        try:
            book = await self._client.get_orderbook(coin, depth)
            return {"success": True, "data": book}
        except Exception as e:
            logger.error(f"get_orderbook error: {e}")
            return {"success": False, "error": str(e)}

    async def get_funding_history(
        self,
        symbol: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get funding rate history"""
        await self.initialize()
        coin = self._normalize_symbol(symbol)
        try:
            history = await self._client.get_funding_history(coin, start_time, end_time)
            return {"success": True, "data": history}
        except Exception as e:
            logger.error(f"get_funding_history error: {e}")
            return {"success": False, "error": str(e)}

    async def get_predicted_funding(self, symbol: str) -> Dict[str, Any]:
        """Get predicted funding rate"""
        await self.initialize()
        coin = self._normalize_symbol(symbol)
        try:
            funding = await self._client.get_predicted_funding(coin)
            return {"success": True, "data": funding}
        except Exception as e:
            logger.error(f"get_predicted_funding error: {e}")
            return {"success": False, "error": str(e)}

    async def modify_order(
        self,
        symbol: str,
        order_id: int,
        side: str,
        qty: float,
        price: float,
        reduce_only: bool = False
    ) -> Dict[str, Any]:
        """Modify an existing order"""
        await self.initialize()
        coin = self._normalize_symbol(symbol)
        is_buy = side.lower() == "buy"
        try:
            result = await self._client.modify_order(
                oid=order_id,
                coin=coin,
                is_buy=is_buy,
                sz=qty,
                limit_px=price,
                reduce_only=reduce_only
            )
            return {
                "retCode": 0 if result.get("status") == "ok" else 1,
                "retMsg": "OK" if result.get("status") == "ok" else str(result),
                "result": result
            }
        except Exception as e:
            logger.error(f"modify_order error: {e}")
            return {"retCode": 1, "retMsg": str(e), "result": {}}

    async def schedule_cancel(self, time_ms: Optional[int] = None) -> Dict[str, Any]:
        """
        Schedule cancel-all (dead man's switch).
        time_ms must be at least 5 seconds in future.
        Pass None to remove scheduled cancel.
        """
        await self.initialize()
        try:
            result = await self._client.schedule_cancel(time_ms)
            return {
                "retCode": 0 if result.get("status") == "ok" else 1,
                "retMsg": "OK" if result.get("status") == "ok" else str(result),
                "result": result
            }
        except Exception as e:
            logger.error(f"schedule_cancel error: {e}")
            return {"retCode": 1, "retMsg": str(e), "result": {}}

    async def transfer_usdc(self, destination: str, amount: float) -> Dict[str, Any]:
        """Transfer USDC to another address"""
        await self.initialize()
        try:
            result = await self._client.transfer_usdc(destination, amount)
            return {
                "retCode": 0 if result.get("status") == "ok" else 1,
                "retMsg": "OK" if result.get("status") == "ok" else str(result),
                "result": result
            }
        except Exception as e:
            logger.error(f"transfer_usdc error: {e}")
            return {"retCode": 1, "retMsg": str(e), "result": {}}

    async def spot_transfer(self, to_perp: bool, amount: float) -> Dict[str, Any]:
        """Transfer USDC between spot and perp accounts"""
        await self.initialize()
        try:
            result = await self._client.spot_transfer(to_perp, amount)
            return {
                "retCode": 0 if result.get("status") == "ok" else 1,
                "retMsg": "OK" if result.get("status") == "ok" else str(result),
                "result": result
            }
        except Exception as e:
            logger.error(f"spot_transfer error: {e}")
            return {"retCode": 1, "retMsg": str(e), "result": {}}

    async def update_isolated_margin(
        self,
        symbol: str,
        is_buy: bool,
        margin_change: float
    ) -> Dict[str, Any]:
        """Add or remove margin from isolated position"""
        await self.initialize()
        coin = self._normalize_symbol(symbol)
        try:
            result = await self._client.update_isolated_margin(coin, is_buy, margin_change)
            return {
                "retCode": 0 if result.get("status") == "ok" else 1,
                "retMsg": "OK" if result.get("status") == "ok" else str(result),
                "result": result
            }
        except Exception as e:
            logger.error(f"update_isolated_margin error: {e}")
            return {"retCode": 1, "retMsg": str(e), "result": {}}

    async def place_twap_order(
        self,
        symbol: str,
        side: str,
        qty: float,
        reduce_only: bool = False,
        duration_minutes: int = 60,
        randomize: bool = False
    ) -> Dict[str, Any]:
        """
        Place TWAP (Time Weighted Average Price) order.
        Splits order into smaller pieces over duration.
        """
        await self.initialize()
        coin = self._normalize_symbol(symbol)
        is_buy = side.lower() == "buy"
        try:
            result = await self._client.place_twap_order(
                coin=coin,
                is_buy=is_buy,
                sz=qty,
                reduce_only=reduce_only,
                duration_minutes=duration_minutes,
                randomize=randomize
            )
            twap_id = None
            if result.get("status") == "ok":
                data = result.get("response", {}).get("data", {})
                status = data.get("status", {})
                if "running" in status:
                    twap_id = status["running"].get("twapId")
            return {
                "retCode": 0 if result.get("status") == "ok" else 1,
                "retMsg": "OK" if result.get("status") == "ok" else str(result),
                "result": {"twapId": twap_id}
            }
        except Exception as e:
            logger.error(f"place_twap_order error: {e}")
            return {"retCode": 1, "retMsg": str(e), "result": {}}

    async def cancel_twap(self, twap_id: int) -> Dict[str, Any]:
        """Cancel a TWAP order"""
        await self.initialize()
        try:
            result = await self._client.cancel_twap(twap_id)
            return {
                "retCode": 0 if result.get("status") == "ok" else 1,
                "retMsg": "OK" if result.get("status") == "ok" else str(result),
                "result": result
            }
        except Exception as e:
            logger.error(f"cancel_twap error: {e}")
            return {"retCode": 1, "retMsg": str(e), "result": {}}

    async def get_symbols(self) -> List[str]:
        """Get list of all tradable symbols"""
        await self.initialize()
        try:
            return await self._client.get_all_symbols()
        except Exception as e:
            logger.error(f"get_symbols error: {e}")
            return []

    async def get_fills_by_time(
        self,
        start_time: int,
        end_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get fills within time range (for pagination)"""
        await self.initialize()
        try:
            fills = await self._client.user_fills(start_time=start_time)
            result_list = []
            for fill in fills:
                if end_time and fill.get("time", 0) > end_time:
                    continue
                result_list.append({
                    "symbol": f"{fill.get('coin', '')}USDC",
                    "side": "Buy" if fill.get("side") == "B" else "Sell",
                    "size": float(fill.get("sz", 0)),
                    "price": float(fill.get("px", 0)),
                    "pnl": float(fill.get("closedPnl", 0)),
                    "fee": float(fill.get("fee", 0)),
                    "time": fill.get("time", 0),
                    "hash": fill.get("hash", ""),
                    "direction": fill.get("dir", ""),
                })
            return {"success": True, "data": result_list}
        except Exception as e:
            logger.error(f"get_fills_by_time error: {e}")
            return {"success": False, "error": str(e)}


async def create_hl_adapter(private_key: str, testnet: bool = False, vault_address: Optional[str] = None) -> HLAdapter:
    adapter = HLAdapter(private_key=private_key, testnet=testnet, vault_address=vault_address)
    await adapter.initialize()
    return adapter
