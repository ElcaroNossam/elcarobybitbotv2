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
from typing import Dict, Any, Optional, List
from datetime import datetime

from exchanges.base import (
    BaseExchange, Balance, Position, Order, OrderResult,
    OrderSide, OrderType, PositionSide
)

logger = logging.getLogger(__name__)


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
        recv_window: int = 5000
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
            await self._session.close()
        self._initialized = False
        logger.info("Bybit exchange connection closed")
    
    def _sign_request(self, params: Dict[str, Any]) -> Dict[str, str]:
        """Create signature for authenticated request"""
        timestamp = str(int(time.time() * 1000))
        
        # Sort and encode parameters
        param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        
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
        
        headers = {}
        if signed:
            headers = self._sign_request(params)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if method == "GET":
                    query = "&".join(f"{k}={v}" for k, v in params.items()) if params else ""
                    full_url = f"{url}?{query}" if query else url
                    async with self._session.get(full_url, headers=headers) as resp:
                        data = await resp.json()
                else:
                    async with self._session.post(url, json=params, headers=headers) as resp:
                        data = await resp.json()
                
                # Check for API errors
                ret_code = data.get("retCode", 0)
                if ret_code != 0:
                    error_msg = data.get("retMsg", "Unknown error")
                    if ret_code == 10002:  # Request timeout
                        if attempt < max_retries - 1:
                            await asyncio.sleep(1)
                            continue
                    raise Exception(f"Bybit API error {ret_code}: {error_msg}")
                
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
        
        account = result.get("list", [{}])[0]
        total_equity = float(account.get("totalEquity", 0))
        available = float(account.get("totalAvailableBalance", 0))
        margin_used = float(account.get("totalInitialMargin", 0))
        unrealized_pnl = float(account.get("totalPerpUPL", 0))
        
        return Balance(
            total_equity=total_equity,
            available_balance=available,
            margin_used=margin_used,
            unrealized_pnl=unrealized_pnl,
            currency="USDT"
        )
    
    async def get_positions(self) -> List[Position]:
        """Get all open positions"""
        result = await self._request(
            "GET",
            "/v5/position/list",
            {"category": "linear", "settleCoin": "USDT"}
        )
        
        positions = []
        for pos in result.get("list", []):
            size = float(pos.get("size", 0))
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
                entry_price=float(pos.get("avgPrice", 0)),
                unrealized_pnl=float(pos.get("unrealisedPnl", 0)),
                leverage=float(pos.get("leverage", 1)),
                margin_mode=pos.get("tradeMode", "cross"),
                liquidation_price=float(pos.get("liqPrice", 0)) or None,
                margin_used=float(pos.get("positionMM", 0))
            ))
        
        return positions
    
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
            size = float(pos.get("size", 0))
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
                entry_price=float(pos.get("avgPrice", 0)),
                unrealized_pnl=float(pos.get("unrealisedPnl", 0)),
                leverage=float(pos.get("leverage", 1)),
                margin_mode=pos.get("tradeMode", "cross"),
                liquidation_price=float(pos.get("liqPrice", 0)) or None,
                margin_used=float(pos.get("positionMM", 0))
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
        size: Optional[float] = None
    ) -> OrderResult:
        """Set take profit for a position"""
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        params = {
            "category": "linear",
            "symbol": symbol,
            "takeProfit": str(price),
            "tpTriggerBy": "LastPrice",
            "tpslMode": "Full" if size is None else "Partial",
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
        size: Optional[float] = None
    ) -> OrderResult:
        """Set stop loss for a position"""
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        params = {
            "category": "linear",
            "symbol": symbol,
            "stopLoss": str(price),
            "slTriggerBy": "LastPrice",
            "tpslMode": "Full" if size is None else "Partial",
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
