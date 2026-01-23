"""
Bybit Exchange Adapter
Implements the BaseExchange interface for Bybit futures trading
"""
import aiohttp
import asyncio
import hashlib
import hmac
import time
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from urllib.parse import quote

from exchanges.base import BaseExchange
from models import (
    Balance, Position, Order, OrderResult,
    OrderSide, OrderType, PositionSide, OrderStatus,
    normalize_symbol as unified_normalize_symbol
)

logger = logging.getLogger(__name__)


def safe_float(val, default=0.0):
    """Safely convert value to float, handling empty strings and None"""
    if val is None or val == '':
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def safe_int(val, default=0):
    """Safely convert value to int, handling empty strings and None"""
    if val is None or val == '':
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


class BybitExchange(BaseExchange):
    """
    Bybit exchange implementation.
    Supports both demo (testnet) and real trading.
    """
    
    MAINNET_URL = "https://api.bybit.com"
    TESTNET_URL = "https://api-testnet.bybit.com"
    DEMO_URL = "https://api-demo.bybit.com"
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        testnet: bool = False,
        demo: bool = True,
        recv_window: int = 60000
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.demo = demo
        self.recv_window = recv_window
        self._session: Optional[aiohttp.ClientSession] = None
        self._initialized = False
        
        # Select base URL
        if demo:
            self.base_url = self.DEMO_URL
        elif testnet:
            self.base_url = self.TESTNET_URL
        else:
            self.base_url = self.MAINNET_URL
    
    @property
    def name(self) -> str:
        mode = "demo" if self.demo else ("testnet" if self.testnet else "mainnet")
        return f"Bybit ({mode})"
    
    async def initialize(self):
        """Initialize the exchange connection"""
        if self._initialized:
            return
        
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"Content-Type": "application/json"}
        )
        self._initialized = True
        logger.info(f"Bybit exchange initialized: {self.base_url}")
    
    async def close(self):
        """Close the exchange connection"""
        if self._session and not self._session.closed:
            try:
                await self._session.close()
                # Wait a bit for the session to fully close
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.debug(f"Error closing Bybit session: {e}")
        self._session = None
        self._initialized = False
    
    def _build_query_string(self, params: Dict[str, Any]) -> str:
        """Build query string with URL-encoded values, sorted alphabetically"""
        if not params:
            return ""
        return "&".join(
            f"{quote(str(k), safe='~')}={quote(str(v), safe='~')}" 
            for k, v in sorted(params.items())
        )
    
    def _sign_request(self, params: Dict[str, Any], is_post: bool = False) -> Dict[str, str]:
        """Create signature for authenticated request"""
        timestamp = str(int(time.time() * 1000))
        
        if is_post:
            # For POST requests, use JSON string
            param_str = json.dumps(params, separators=(',', ':')) if params else ""
        else:
            # For GET requests, use query string format with URL encoding
            param_str = self._build_query_string(params)
        
        # Create signature string
        sign_str = f"{timestamp}{self.api_key}{self.recv_window}{param_str}"
        
        # Calculate HMAC signature
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            sign_str.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        return {
            "X-BAPI-API-KEY": self.api_key,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-RECV-WINDOW": str(self.recv_window),
            "X-BAPI-SIGN": signature
        }
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict[str, Any] = None,
        signed: bool = True
    ) -> Dict[str, Any]:
        """Make API request with retry logic"""
        if not self._initialized:
            await self.initialize()
        
        params = params or {}
        url = f"{self.base_url}{endpoint}"
        
        headers = {"Content-Type": "application/json"}
        if signed:
            is_post = method.upper() == "POST"
            sign_headers = self._sign_request(params, is_post=is_post)
            headers.update(sign_headers)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if method == "GET":
                    # Use same query string format as signature (sorted + URL-encoded)
                    query = self._build_query_string(params)
                    full_url = f"{url}?{query}" if query else url
                    async with self._session.get(full_url, headers=headers) as resp:
                        data = await resp.json()
                else:
                    body = json.dumps(params, separators=(',', ':')) if params else ""
                    async with self._session.post(url, data=body, headers=headers) as resp:
                        data = await resp.json()
                
                # Handle None response (common on testnet with no data)
                if data is None:
                    logger.debug(f"Bybit API returned None for {endpoint} (testnet or empty)")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1)
                        continue
                    return {}
                
                # Check for API errors
                ret_code = data.get("retCode", 0)
                if ret_code != 0:
                    error_msg = data.get("retMsg", "Unknown error")
                    if ret_code == 10002:  # Request timeout
                        if attempt < max_retries - 1:
                            await asyncio.sleep(1)
                            continue
                    from core.exceptions import ExchangeError
                    raise ExchangeError(f"Bybit API error {ret_code}: {error_msg}")
                
                return data.get("result", {})
                
            except aiohttp.ClientError as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                else:
                    raise
        
        return {}
    
    async def get_balance(self) -> Balance:
        """Get account balance"""
        result = await self._request(
            "GET",
            "/v5/account/wallet-balance",
            {"accountType": "UNIFIED"}
        )
        
        # SECURITY: Safe access - handle None and empty list
        list_data = result.get("list") or [{}]
        account = list_data[0] if list_data else {}
        
        def safe_float(val, default=0.0):
            if val is None or val == '':
                return default
            try:
                return float(val)
            except (ValueError, TypeError):
                return default
        
        total_equity = safe_float(account.get("totalEquity"))
        available = safe_float(account.get("totalAvailableBalance"))
        margin_used = safe_float(account.get("totalInitialMargin"))
        unrealized_pnl = safe_float(account.get("totalPerpUPL"))
        
        return Balance(
            total_equity=total_equity,
            available_balance=available,
            margin_used=margin_used,
            unrealized_pnl=unrealized_pnl,
            currency="USDT"
        )
    
    async def get_positions(self) -> List[Position]:
        """Get all open positions (with pagination if needed)"""
        all_positions = []
        cursor = None
        
        while True:
            params = {"category": "linear", "settleCoin": "USDT", "limit": 200}
            if cursor:
                params["cursor"] = cursor
            
            result = await self._request("GET", "/v5/position/list", params)
        
            positions = []
            for pos in result.get("list", []):
                size = safe_float(pos.get("size"), 0)
                if size == 0:
                    continue
            
                side_str = pos.get("side", "None")
                if side_str == "Buy":
                    side = PositionSide.LONG
                elif side_str == "Sell":
                    side = PositionSide.SHORT
                else:
                    side = PositionSide.NONE
            
                positions.append(Position(
                    symbol=pos.get("symbol", ""),
                    side=side,
                    size=size,
                    entry_price=safe_float(pos.get("avgPrice"), 0),
                    unrealized_pnl=safe_float(pos.get("unrealisedPnl"), 0),
                    leverage=safe_float(pos.get("leverage"), 1),
                    margin_mode=pos.get("tradeMode", "cross"),
                    liquidation_price=safe_float(pos.get("liqPrice")) or None,
                    margin_used=safe_float(pos.get("positionIM"), 0),  # Fixed: was positionMM, now positionIM (initial margin)
                    mark_price=safe_float(pos.get("markPrice"), 0),
                    stop_loss=safe_float(pos.get("stopLoss")) or None,
                    take_profit=safe_float(pos.get("takeProfit")) or None
                ))
            
            all_positions.extend(positions)
            
            # Check for next page
            cursor = result.get("nextPageCursor")
            if not cursor:
                break
        
        return all_positions
    
    async def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for specific symbol"""
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        result = await self._request(
            "GET",
            "/v5/position/list",
            {"category": "linear", "symbol": symbol}
        )
        
        for pos in result.get("list", []):
            size = safe_float(pos.get("size"), 0)
            if size == 0:
                continue
            
            side_str = pos.get("side", "None")
            if side_str == "Buy":
                side = PositionSide.LONG
            elif side_str == "Sell":
                side = PositionSide.SHORT
            else:
                side = PositionSide.NONE
            
            return Position(
                symbol=pos.get("symbol", ""),
                side=side,
                size=size,
                entry_price=safe_float(pos.get("avgPrice"), 0),
                unrealized_pnl=safe_float(pos.get("unrealisedPnl"), 0),
                leverage=safe_float(pos.get("leverage"), 1),
                margin_mode=pos.get("tradeMode", "cross"),
                liquidation_price=safe_float(pos.get("liqPrice")) or None,
                margin_used=safe_float(pos.get("positionIM"), 0)  # Fixed: was positionMM, now positionIM
            )
        
        return None
    
    async def place_order(
        self,
        symbol: str,
        side: OrderSide,
        size: float,
        price: Optional[float] = None,
        order_type: OrderType = OrderType.MARKET,
        reduce_only: bool = False,
        client_order_id: Optional[str] = None
    ) -> OrderResult:
        """Place a new order"""
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        params = {
            "category": "linear",
            "symbol": symbol,
            "side": side.value,
            "orderType": order_type.value,
            "qty": str(size),
            "timeInForce": "GTC" if order_type == OrderType.LIMIT else "IOC",
            "reduceOnly": reduce_only,
        }
        
        if price and order_type == OrderType.LIMIT:
            params["price"] = str(price)
        
        if client_order_id:
            params["orderLinkId"] = client_order_id
        
        try:
            result = await self._request("POST", "/v5/order/create", params)
            
            return OrderResult(
                success=True,
                order_id=result.get("orderId"),
                avg_price=float(result.get("avgPrice", 0)) or None
            )
        except Exception as e:
            logger.error(f"Order placement failed: {e}")
            return OrderResult(success=False, error=str(e))
    
    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel an order"""
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        try:
            await self._request(
                "POST",
                "/v5/order/cancel",
                {
                    "category": "linear",
                    "symbol": symbol,
                    "orderId": order_id
                }
            )
            return True
        except Exception as e:
            logger.error(f"Order cancellation failed: {e}")
            return False
    
    async def cancel_all_orders(self, symbol: Optional[str] = None) -> int:
        """Cancel all orders"""
        params = {"category": "linear"}
        
        if symbol:
            symbol = symbol.upper()
            if not symbol.endswith("USDT"):
                symbol = f"{symbol}USDT"
            params["symbol"] = symbol
        
        try:
            result = await self._request("POST", "/v5/order/cancel-all", params)
            return len(result.get("list", []))
        except Exception as e:
            logger.error(f"Cancel all orders failed: {e}")
            return 0
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """Get all open orders"""
        params = {"category": "linear"}
        
        if symbol:
            symbol = symbol.upper()
            if not symbol.endswith("USDT"):
                symbol = f"{symbol}USDT"
            params["symbol"] = symbol
        else:
            # settleCoin required when no symbol specified
            params["settleCoin"] = "USDT"
        
        result = await self._request("GET", "/v5/order/realtime", params)
        
        orders = []
        for o in result.get("list", []):
            side = OrderSide.BUY if o.get("side") == "Buy" else OrderSide.SELL
            order_type = OrderType.LIMIT if o.get("orderType") == "Limit" else OrderType.MARKET
            
            orders.append(Order(
                order_id=o.get("orderId", ""),
                symbol=o.get("symbol", ""),
                side=side,
                order_type=order_type,
                size=float(o.get("qty", 0)),
                price=float(o.get("price", 0)) or None,
                filled_size=float(o.get("cumExecQty", 0)),
                status=o.get("orderStatus", ""),
                reduce_only=o.get("reduceOnly", False),
                client_order_id=o.get("orderLinkId"),
                created_at=int(o.get("createdTime", 0))
            ))
        
        return orders
    
    async def set_leverage(self, symbol: str, leverage: int) -> bool:
        """Set leverage for a symbol"""
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        try:
            await self._request(
                "POST",
                "/v5/position/set-leverage",
                {
                    "category": "linear",
                    "symbol": symbol,
                    "buyLeverage": str(leverage),
                    "sellLeverage": str(leverage)
                }
            )
            return True
        except Exception as e:
            # Ignore if leverage is already set
            if "leverage not modified" in str(e).lower():
                return True
            logger.error(f"Set leverage failed: {e}")
            return False
    
    async def set_take_profit(
        self,
        symbol: str,
        price: float,
        size: Optional[float] = None,
        position_idx: int = 0
    ) -> OrderResult:
        """Set take profit for a position"""
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        params = {
            "category": "linear",
            "symbol": symbol,
            "takeProfit": str(price),
            "tpTriggerBy": "MarkPrice",  # More reliable than LastPrice
            "tpslMode": "Full" if size is None else "Partial",
            "positionIdx": position_idx,
        }
        
        if size:
            params["tpSize"] = str(size)
        
        try:
            result = await self._request("POST", "/v5/position/trading-stop", params)
            return OrderResult(success=True)
        except Exception as e:
            logger.error(f"Set take profit failed: {e}")
            return OrderResult(success=False, error=str(e))
    
    async def set_stop_loss(
        self,
        symbol: str,
        price: float,
        size: Optional[float] = None,
        position_idx: int = 0
    ) -> OrderResult:
        """Set stop loss for a position"""
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        params = {
            "category": "linear",
            "symbol": symbol,
            "stopLoss": str(price),
            "slTriggerBy": "MarkPrice",  # More reliable than LastPrice
            "tpslMode": "Full" if size is None else "Partial",
            "positionIdx": position_idx,
        }
        
        if size:
            params["slSize"] = str(size)
        
        try:
            result = await self._request("POST", "/v5/position/trading-stop", params)
            return OrderResult(success=True)
        except Exception as e:
            logger.error(f"Set stop loss failed: {e}")
            return OrderResult(success=False, error=str(e))
    
    async def close_position(
        self,
        symbol: str,
        size: Optional[float] = None
    ) -> OrderResult:
        """Close a position"""
        position = await self.get_position(symbol)
        
        if not position or position.size == 0:
            return OrderResult(success=False, error="No position found")
        
        close_size = size or position.size
        
        # Opposite side to close
        if position.side == PositionSide.LONG:
            side = OrderSide.SELL
        else:
            side = OrderSide.BUY
        
        return await self.place_order(
            symbol=symbol,
            side=side,
            size=close_size,
            order_type=OrderType.MARKET,
            reduce_only=True
        )
    
    async def get_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        result = await self._request(
            "GET",
            "/v5/market/tickers",
            {"category": "linear", "symbol": symbol},
            signed=False
        )
        
        tickers = result.get("list", [])
        if tickers:
            return float(tickers[0].get("lastPrice", 0))
        
        return None
    
    async def get_orderbook(self, symbol: str, depth: int = 10) -> Dict[str, Any]:
        """Get orderbook for a symbol"""
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        result = await self._request(
            "GET",
            "/v5/market/orderbook",
            {"category": "linear", "symbol": symbol, "limit": depth},
            signed=False
        )
        
        return {
            "bids": [[float(b[0]), float(b[1])] for b in result.get("b", [])],
            "asks": [[float(a[0]), float(a[1])] for a in result.get("a", [])],
            "timestamp": result.get("ts", 0)
        }
    
    async def get_symbols(self) -> List[str]:
        """Get list of all tradable symbols"""
        result = await self._request(
            "GET",
            "/v5/market/instruments-info",
            {"category": "linear"},
            signed=False
        )
        
        symbols = []
        for item in result.get("list", []):
            if item.get("status") == "Trading":
                symbols.append(item.get("symbol", ""))
        
        return symbols
    
    # Alias for compatibility
    async def get_ticker(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get ticker info (alias for get_price with extended data)"""
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        result = await self._request(
            "GET",
            "/v5/market/tickers",
            {"category": "linear", "symbol": symbol},
            signed=False
        )
        
        tickers = result.get("list", [])
        if tickers:
            t = tickers[0]
            return {
                "symbol": t.get("symbol"),
                "price": float(t.get("lastPrice", 0)),
                "bid": float(t.get("bid1Price", 0)),
                "ask": float(t.get("ask1Price", 0)),
                "volume_24h": float(t.get("volume24h", 0)),
                "high_24h": float(t.get("highPrice24h", 0)),
                "low_24h": float(t.get("lowPrice24h", 0)),
                "change_24h": float(t.get("price24hPcnt", 0)) * 100,
            }
        return None
    
    # ==================== EXTENDED API METHODS ====================
    
    async def get_candles(
        self,
        symbol: str,
        interval: str = "15",
        limit: int = 200,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get candlestick/kline data
        
        interval: 1,3,5,15,30,60,120,240,360,720,D,W,M
        """
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        params = {
            "category": "linear",
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        if start_time:
            params["start"] = start_time
        if end_time:
            params["end"] = end_time
        
        result = await self._request(
            "GET",
            "/v5/market/kline",
            params,
            signed=False
        )
        
        candles = []
        for c in result.get("list", []):
            candles.append({
                "timestamp": int(c[0]),
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4]),
                "volume": float(c[5]),
                "turnover": float(c[6]) if len(c) > 6 else 0
            })
        
        return candles
    
    async def get_trade_history(
        self,
        symbol: Optional[str] = None,
        order_id: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get user's trade history (fills)"""
        params = {
            "category": "linear",
            "limit": limit
        }
        
        if symbol:
            symbol = symbol.upper()
            if not symbol.endswith("USDT"):
                symbol = f"{symbol}USDT"
            params["symbol"] = symbol
        
        if order_id:
            params["orderId"] = order_id
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        
        result = await self._request("GET", "/v5/execution/list", params)
        
        trades = []
        for t in result.get("list", []):
            trades.append({
                "exec_id": t.get("execId"),
                "order_id": t.get("orderId"),
                "symbol": t.get("symbol"),
                "side": t.get("side"),
                "price": float(t.get("execPrice", 0)),
                "qty": float(t.get("execQty", 0)),
                "fee": float(t.get("execFee", 0)),
                "exec_type": t.get("execType"),  # Trade, Funding, etc
                "timestamp": int(t.get("execTime", 0))
            })
        
        return trades
    
    async def get_order_history(
        self,
        symbol: Optional[str] = None,
        order_status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get historical orders"""
        params = {
            "category": "linear",
            "limit": limit
        }
        
        if symbol:
            symbol = symbol.upper()
            if not symbol.endswith("USDT"):
                symbol = f"{symbol}USDT"
            params["symbol"] = symbol
        
        if order_status:
            params["orderStatus"] = order_status
        
        result = await self._request("GET", "/v5/order/history", params)
        
        orders = []
        for o in result.get("list", []):
            orders.append({
                "order_id": o.get("orderId"),
                "symbol": o.get("symbol"),
                "side": o.get("side"),
                "order_type": o.get("orderType"),
                "price": safe_float(o.get("price")) or None,
                "qty": safe_float(o.get("qty")),
                "filled_qty": safe_float(o.get("cumExecQty")),
                "avg_price": safe_float(o.get("avgPrice")) or None,
                "status": o.get("orderStatus"),
                "reduce_only": o.get("reduceOnly", False),
                "created_at": safe_int(o.get("createdTime")),
                "updated_at": safe_int(o.get("updatedTime"))
            })
        
        return orders
    
    async def get_pnl_history(
        self,
        symbol: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get closed P&L history"""
        params = {
            "category": "linear",
            "limit": limit
        }
        
        if symbol:
            symbol = symbol.upper()
            if not symbol.endswith("USDT"):
                symbol = f"{symbol}USDT"
            params["symbol"] = symbol
        
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        
        result = await self._request("GET", "/v5/position/closed-pnl", params)
        
        pnls = []
        for p in result.get("list", []):
            pnls.append({
                "symbol": p.get("symbol"),
                "side": p.get("side"),
                "qty": float(p.get("qty", 0)),
                "entry_price": float(p.get("avgEntryPrice", 0)),
                "exit_price": float(p.get("avgExitPrice", 0)),
                "closed_pnl": float(p.get("closedPnl", 0)),
                "leverage": int(p.get("leverage", 1)),
                "created_at": int(p.get("createdTime", 0)),
                "updated_at": int(p.get("updatedTime", 0))
            })
        
        return pnls
    
    async def modify_order(
        self,
        symbol: str,
        order_id: str,
        price: Optional[float] = None,
        qty: Optional[float] = None
    ) -> bool:
        """Modify an existing order"""
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        params = {
            "category": "linear",
            "symbol": symbol,
            "orderId": order_id
        }
        
        if price is not None:
            params["price"] = str(price)
        if qty is not None:
            params["qty"] = str(qty)
        
        try:
            await self._request("POST", "/v5/order/amend", params)
            return True
        except Exception as e:
            logger.error(f"Modify order failed: {e}")
            return False
    
    async def get_wallet_balance(self) -> Dict[str, Any]:
        """Get detailed wallet balance for all coins"""
        result = await self._request(
            "GET",
            "/v5/account/wallet-balance",
            {"accountType": "UNIFIED"}
        )
        
        # SECURITY: Safe access - handle None and empty list
        list_data = result.get("list") or [{}]
        account = list_data[0] if list_data else {}
        coins = []
        for coin in account.get("coin", []):
            equity = safe_float(coin.get("equity"))
            if equity > 0:
                coins.append({
                    "coin": coin.get("coin"),
                    "equity": equity,
                    "available": safe_float(coin.get("availableToWithdraw")),
                    "wallet_balance": safe_float(coin.get("walletBalance")),
                    "unrealized_pnl": safe_float(coin.get("unrealisedPnl")),
                    "usd_value": safe_float(coin.get("usdValue"))
                })
        
        return {
            "total_equity": safe_float(account.get("totalEquity")),
            "total_available": safe_float(account.get("totalAvailableBalance")),
            "total_margin_used": safe_float(account.get("totalInitialMargin")),
            "total_unrealized_pnl": safe_float(account.get("totalPerpUPL")),
            "coins": coins
        }
    
    async def get_funding_history(
        self,
        symbol: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get funding fee history"""
        params = {
            "category": "linear",
            "limit": limit
        }
        
        if symbol:
            symbol = symbol.upper()
            if not symbol.endswith("USDT"):
                symbol = f"{symbol}USDT"
            params["symbol"] = symbol
        
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        
        result = await self._request("GET", "/v5/execution/list", params)
        
        # Filter only funding executions
        fundings = []
        for t in result.get("list", []):
            if t.get("execType") == "Funding":
                fundings.append({
                    "symbol": t.get("symbol"),
                    "side": t.get("side"),
                    "size": float(t.get("execQty", 0)),
                    "funding_rate": float(t.get("feeRate", 0)),
                    "funding_fee": float(t.get("execFee", 0)),
                    "timestamp": int(t.get("execTime", 0))
                })
        
        return fundings
    
    async def get_current_funding_rate(self, symbol: str) -> Dict[str, Any]:
        """Get current funding rate for a symbol"""
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        result = await self._request(
            "GET",
            "/v5/market/tickers",
            {"category": "linear", "symbol": symbol},
            signed=False
        )
        
        tickers = result.get("list", [])
        if tickers:
            t = tickers[0]
            return {
                "symbol": t.get("symbol"),
                "funding_rate": float(t.get("fundingRate", 0)),
                "next_funding_time": int(t.get("nextFundingTime", 0))
            }
        
        return {}
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account configuration info"""
        result = await self._request("GET", "/v5/account/info", {})
        
        return {
            "margin_mode": result.get("marginMode"),
            "unified_margin_status": result.get("unifiedMarginStatus"),
            "updated_time": result.get("updatedTime")
        }
    
    async def set_margin_mode(self, symbol: str, margin_mode: str = "ISOLATED") -> bool:
        """Set margin mode for a symbol (ISOLATED or CROSS)"""
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        trade_mode = 1 if margin_mode.upper() == "ISOLATED" else 0
        
        try:
            await self._request(
                "POST",
                "/v5/position/switch-isolated",
                {
                    "category": "linear",
                    "symbol": symbol,
                    "tradeMode": trade_mode,
                    "buyLeverage": "10",
                    "sellLeverage": "10"
                }
            )
            return True
        except Exception as e:
            if "margin mode is not modified" in str(e).lower() or "110026" in str(e):
                return True
            logger.error(f"Set margin mode failed: {e}")
            return False
    
    async def set_position_mode(self, mode: str = "MergedSingle") -> bool:
        """Set position mode (MergedSingle or BothSide)"""
        try:
            await self._request(
                "POST",
                "/v5/position/switch-mode",
                {
                    "category": "linear",
                    "mode": 0 if mode == "MergedSingle" else 3
                }
            )
            return True
        except Exception as e:
            if "position mode is not modified" in str(e).lower():
                return True
            logger.error(f"Set position mode failed: {e}")
            return False
    
    async def get_fee_rates(self, symbol: Optional[str] = None) -> Dict[str, float]:
        """Get trading fee rates"""
        params = {"category": "linear"}
        if symbol:
            symbol = symbol.upper()
            if not symbol.endswith("USDT"):
                symbol = f"{symbol}USDT"
            params["symbol"] = symbol
        else:
            # Symbol is required for fee-rate endpoint
            params["symbol"] = "BTCUSDT"
        
        try:
            result = await self._request("GET", "/v5/account/fee-rate", params)
            
            # SECURITY: Safe access - handle None and empty list
            list_data = result.get("list") or [{}]
            fees = list_data[0] if list_data else {}
            return {
                "symbol": fees.get("symbol", "default"),
                "taker_fee": safe_float(fees.get("takerFeeRate")),
                "maker_fee": safe_float(fees.get("makerFeeRate"))
            }
        except Exception as e:
            # Fee rate API may not be available on demo
            logger.warning(f"get_fee_rates failed: {e}")
            return {
                "symbol": symbol or "default",
                "taker_fee": 0.0006,  # Default Bybit taker fee
                "maker_fee": 0.0001   # Default Bybit maker fee
            }
    
    async def get_instrument_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get detailed instrument info for a symbol"""
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        result = await self._request(
            "GET",
            "/v5/market/instruments-info",
            {"category": "linear", "symbol": symbol},
            signed=False
        )
        
        instruments = result.get("list", [])
        if instruments:
            i = instruments[0]
            return {
                "symbol": i.get("symbol"),
                "base_coin": i.get("baseCoin"),
                "quote_coin": i.get("quoteCoin"),
                "status": i.get("status"),
                "min_leverage": float(i.get("leverageFilter", {}).get("minLeverage", 1)),
                "max_leverage": float(i.get("leverageFilter", {}).get("maxLeverage", 100)),
                "leverage_step": float(i.get("leverageFilter", {}).get("leverageStep", 0.01)),
                "min_order_qty": float(i.get("lotSizeFilter", {}).get("minOrderQty", 0)),
                "max_order_qty": float(i.get("lotSizeFilter", {}).get("maxOrderQty", 0)),
                "qty_step": float(i.get("lotSizeFilter", {}).get("qtyStep", 0)),
                "min_price": float(i.get("priceFilter", {}).get("minPrice", 0)),
                "max_price": float(i.get("priceFilter", {}).get("maxPrice", 0)),
                "tick_size": float(i.get("priceFilter", {}).get("tickSize", 0))
            }
        
        return None
    
    async def get_server_time(self) -> int:
        """Get Bybit server time"""
        result = await self._request(
            "GET",
            "/v5/market/time",
            {},
            signed=False
        )
        return int(result.get("timeSecond", 0)) * 1000
    
    async def get_open_interest(self, symbol: str) -> Dict[str, Any]:
        """Get open interest for a symbol"""
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        result = await self._request(
            "GET",
            "/v5/market/open-interest",
            {"category": "linear", "symbol": symbol, "intervalTime": "5min", "limit": 1},
            signed=False
        )
        
        # SECURITY: Safe access - handle None and empty list
        list_data = result.get("list") or [{}]
        data = list_data[0] if list_data else {}
        return {
            "symbol": data.get("symbol"),
            "open_interest": float(data.get("openInterest", 0)),
            "timestamp": int(data.get("timestamp", 0))
        }
    
    async def get_risk_limit(self, symbol: str) -> List[Dict[str, Any]]:
        """Get risk limit tiers for a symbol"""
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        result = await self._request(
            "GET",
            "/v5/market/risk-limit",
            {"category": "linear", "symbol": symbol},
            signed=False
        )
        
        tiers = []
        for r in result.get("list", []):
            tiers.append({
                "id": r.get("id"),
                "symbol": r.get("symbol"),
                "max_leverage": float(r.get("maxLeverage", 0)),
                "risk_limit_value": float(r.get("riskLimitValue", 0)),
                "maintenance_margin": float(r.get("maintainMargin", 0)),
                "initial_margin": float(r.get("initialMargin", 0))
            })
        
        return tiers
