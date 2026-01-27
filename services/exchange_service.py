"""
Exchange Service - Abstract adapter pattern for Bybit and HyperLiquid
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum
import aiohttp
import hashlib
import hmac
import time
import json

from models.exchange_credentials import ExchangeCredentials, ExchangeType
from models.position import Position, PositionSide
from core.exceptions import (
    ExchangeError, AuthenticationError, RateLimitError,
    InsufficientBalanceError, PremiumRequiredError, ExchangeNotConnectedError
)


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_MARKET = "stop_market"
    STOP_LIMIT = "stop_limit"
    TAKE_PROFIT = "take_profit"
    STOP_LOSS = "stop_loss"


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


@dataclass
class OrderResult:
    """Result of order placement"""
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float]
    status: str
    filled_qty: float = 0.0
    avg_price: float = 0.0
    error: Optional[str] = None
    raw_response: Optional[Dict] = None


@dataclass
class AccountBalance:
    """Account balance info"""
    total_equity: float
    available_balance: float
    used_margin: float
    unrealized_pnl: float
    currency: str = "USDT"


class ExchangeAdapter(ABC):
    """Abstract base class for exchange adapters"""
    
    def __init__(self, credentials: ExchangeCredentials):
        self.credentials = credentials
        self._session: Optional[aiohttp.ClientSession] = None
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection and verify credentials"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection"""
        pass
    
    @abstractmethod
    async def get_balance(self) -> AccountBalance:
        """Get account balance"""
        pass
    
    @abstractmethod
    async def get_positions(self) -> List[Position]:
        """Get all open positions"""
        pass
    
    @abstractmethod
    async def place_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        take_profit: Optional[float] = None,
        stop_loss: Optional[float] = None,
        leverage: int = 1,
        reduce_only: bool = False
    ) -> OrderResult:
        """Place an order"""
        pass
    
    @abstractmethod
    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel an order"""
        pass
    
    @abstractmethod
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get open orders"""
        pass
    
    @abstractmethod
    async def set_leverage(self, symbol: str, leverage: int) -> bool:
        """Set leverage for a symbol"""
        pass
    
    @abstractmethod
    async def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker price"""
        pass
    
    @property
    @abstractmethod
    def exchange_type(self) -> ExchangeType:
        """Return exchange type"""
        pass


class BybitAdapter(ExchangeAdapter):
    """Bybit exchange adapter"""
    
    DEMO_BASE_URL = "https://api-demo.bybit.com"
    REAL_BASE_URL = "https://api.bybit.com"
    
    def __init__(self, credentials: ExchangeCredentials, is_demo: bool = True):
        super().__init__(credentials)
        self.is_demo = is_demo
        self.base_url = self.DEMO_BASE_URL if is_demo else self.REAL_BASE_URL
    
    @property
    def exchange_type(self) -> ExchangeType:
        return ExchangeType.BYBIT
    
    def _sign_request(self, params: Dict, timestamp: int) -> str:
        """Create HMAC signature for Bybit API"""
        param_str = str(timestamp) + self.credentials.api_key + "5000"
        if params:
            param_str += json.dumps(params, separators=(",", ":"))
        return hmac.new(
            self.credentials.get_decrypted_secret().encode("utf-8"),
            param_str.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        body: Optional[Dict] = None
    ) -> Dict:
        """Make authenticated request to Bybit API"""
        if not self._session:
            self._session = aiohttp.ClientSession()
        
        timestamp = int(time.time() * 1000)
        headers = {
            "X-BAPI-API-KEY": self.credentials.api_key,
            "X-BAPI-TIMESTAMP": str(timestamp),
            "X-BAPI-RECV-WINDOW": "5000",
            "Content-Type": "application/json"
        }
        
        sign_params = body if body else params
        headers["X-BAPI-SIGN"] = self._sign_request(sign_params or {}, timestamp)
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self._session.request(
                method, url, headers=headers,
                params=params if method == "GET" else None,
                json=body if method == "POST" else None
            ) as resp:
                data = await resp.json()
                
                if data.get("retCode") != 0:
                    error_msg = data.get("retMsg", "Unknown error")
                    if "auth" in error_msg.lower() or "key" in error_msg.lower():
                        raise AuthenticationError(error_msg)
                    if "rate" in error_msg.lower():
                        raise RateLimitError(error_msg)
                    if "insufficient" in error_msg.lower():
                        raise InsufficientBalanceError(error_msg)
                    raise ExchangeError(error_msg)
                
                return data.get("result", {})
        except aiohttp.ClientError as e:
            raise ExchangeError(f"Network error: {str(e)}")
    
    async def connect(self) -> bool:
        """Test connection to Bybit"""
        try:
            await self.get_balance()
            return True
        except Exception:
            return False
    
    async def disconnect(self) -> None:
        """Close session"""
        if self._session:
            await self._session.close()
            self._session = None
    
    async def get_balance(self) -> AccountBalance:
        """Get Bybit account balance"""
        result = await self._request("GET", "/v5/account/wallet-balance", {"accountType": "UNIFIED"})
        
        if result.get("list"):
            account = result["list"][0]
            return AccountBalance(
                total_equity=float(account.get("totalEquity", 0)),
                available_balance=float(account.get("totalAvailableBalance", 0)),
                used_margin=float(account.get("totalMarginBalance", 0)),
                unrealized_pnl=float(account.get("totalPerpUPL", 0)),
            )
        return AccountBalance(0, 0, 0, 0)
    
    async def get_positions(self) -> List[Position]:
        """Get Bybit positions"""
        result = await self._request("GET", "/v5/position/list", {"category": "linear", "settleCoin": "USDT"})
        positions = []
        
        for pos in result.get("list", []):
            if float(pos.get("size", 0)) > 0:
                positions.append(Position(
                    symbol=pos["symbol"],
                    side=PositionSide.LONG if pos["side"] == "Buy" else PositionSide.SHORT,
                    size=float(pos["size"]),
                    entry_price=float(pos["avgPrice"]),
                    current_price=float(pos.get("markPrice", 0)),
                    leverage=int(float(pos.get("leverage", 1))),
                    unrealized_pnl=float(pos.get("unrealisedPnl", 0)),
                    margin=float(pos.get("positionIM", 0)),
                    liquidation_price=float(pos.get("liqPrice", 0)) if pos.get("liqPrice") else None,
                    take_profit=float(pos.get("takeProfit", 0)) if pos.get("takeProfit") else None,
                    stop_loss=float(pos.get("stopLoss", 0)) if pos.get("stopLoss") else None,
                    exchange=ExchangeType.BYBIT
                ))
        return positions
    
    async def place_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        take_profit: Optional[float] = None,
        stop_loss: Optional[float] = None,
        leverage: int = 1,
        reduce_only: bool = False
    ) -> OrderResult:
        """Place order on Bybit"""
        body = {
            "category": "linear",
            "symbol": symbol,
            "side": "Buy" if side == OrderSide.BUY else "Sell",
            "orderType": "Market" if order_type == OrderType.MARKET else "Limit",
            "qty": str(quantity),
            "reduceOnly": reduce_only,
        }
        
        if price and order_type == OrderType.LIMIT:
            body["price"] = str(price)
        if take_profit:
            body["takeProfit"] = str(take_profit)
        if stop_loss:
            body["stopLoss"] = str(stop_loss)
        
        try:
            result = await self._request("POST", "/v5/order/create", body=body)
            return OrderResult(
                order_id=result.get("orderId", ""),
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                status="created",
                raw_response=result
            )
        except ExchangeError as e:
            return OrderResult(
                order_id="",
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                status="error",
                error=str(e)
            )
    
    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel order on Bybit"""
        try:
            await self._request("POST", "/v5/order/cancel", body={
                "category": "linear",
                "symbol": symbol,
                "orderId": order_id
            })
            return True
        except ExchangeError:
            return False
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get open orders from Bybit"""
        params = {"category": "linear"}
        if symbol:
            params["symbol"] = symbol
        result = await self._request("GET", "/v5/order/realtime", params)
        return result.get("list", [])
    
    async def set_leverage(self, symbol: str, leverage: int) -> bool:
        """Set leverage on Bybit"""
        try:
            await self._request("POST", "/v5/position/set-leverage", body={
                "category": "linear",
                "symbol": symbol,
                "buyLeverage": str(leverage),
                "sellLeverage": str(leverage)
            })
            return True
        except ExchangeError:
            return False
    
    async def get_ticker(self, symbol: str) -> Dict:
        """Get ticker from Bybit"""
        result = await self._request("GET", "/v5/market/tickers", {"category": "linear", "symbol": symbol})
        if result.get("list"):
            return result["list"][0]
        return {}


class HyperLiquidAdapter(ExchangeAdapter):
    """HyperLiquid exchange adapter - PREMIUM ONLY"""
    
    BASE_URL = "https://api.hyperliquid.xyz"
    
    def __init__(self, credentials: ExchangeCredentials):
        super().__init__(credentials)
        self._is_premium_verified = False
    
    @property
    def exchange_type(self) -> ExchangeType:
        return ExchangeType.HYPERLIQUID
    
    def _check_premium(self) -> None:
        """Verify premium access for HyperLiquid"""
        if not self._is_premium_verified:
            raise PremiumRequiredError("HyperLiquid trading requires Premium license")
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None
    ) -> Dict:
        """Make request to HyperLiquid API"""
        self._check_premium()
        
        if not self._session:
            self._session = aiohttp.ClientSession()
        
        url = f"{self.BASE_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        try:
            async with self._session.request(
                method, url, headers=headers, json=data
            ) as resp:
                return await resp.json()
        except aiohttp.ClientError as e:
            raise ExchangeError(f"HyperLiquid network error: {str(e)}")
    
    async def connect(self) -> bool:
        """Test connection to HyperLiquid"""
        self._check_premium()
        try:
            await self.get_balance()
            self._is_premium_verified = True
            return True
        except Exception:
            return False
    
    async def disconnect(self) -> None:
        """Close session"""
        if self._session:
            await self._session.close()
            self._session = None
    
    async def get_balance(self) -> AccountBalance:
        """Get HyperLiquid account balance"""
        self._check_premium()
        data = await self._request("POST", "/info", {
            "type": "clearinghouseState",
            "user": self.credentials.wallet_address
        })
        
        margin_summary = data.get("marginSummary", {})
        return AccountBalance(
            total_equity=float(margin_summary.get("accountValue", 0)),
            available_balance=float(margin_summary.get("availableBalance", 0)),
            used_margin=float(margin_summary.get("totalMarginUsed", 0)),
            unrealized_pnl=float(margin_summary.get("totalUnrealizedPnl", 0)),
        )
    
    async def get_positions(self) -> List[Position]:
        """Get HyperLiquid positions"""
        self._check_premium()
        data = await self._request("POST", "/info", {
            "type": "clearinghouseState",
            "user": self.credentials.wallet_address
        })
        
        positions = []
        for pos in data.get("assetPositions", []):
            p = pos.get("position", {})
            size = float(p.get("szi", 0))
            if abs(size) > 0:
                positions.append(Position(
                    symbol=p.get("coin", ""),
                    side=PositionSide.LONG if size > 0 else PositionSide.SHORT,
                    size=abs(size),
                    entry_price=float(p.get("entryPx", 0)),
                    current_price=float(p.get("positionValue", 0)) / abs(size) if size else 0,
                    leverage=int(float(p.get("leverage", {}).get("value", 1))),
                    unrealized_pnl=float(p.get("unrealizedPnl", 0)),
                    margin=float(p.get("marginUsed", 0)),
                    liquidation_price=float(p.get("liquidationPx", 0)) if p.get("liquidationPx") else None,
                    exchange=ExchangeType.HYPERLIQUID
                ))
        return positions
    
    async def place_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        take_profit: Optional[float] = None,
        stop_loss: Optional[float] = None,
        leverage: int = 1,
        reduce_only: bool = False
    ) -> OrderResult:
        """Place order on HyperLiquid using exchange action endpoint"""
        self._check_premium()
        
        # HyperLiquid order format
        is_buy = side == OrderSide.BUY
        order_request = {
            "type": "order",
            "orders": [{
                "a": symbol.replace("USDT", ""),  # Asset (e.g., BTC, ETH)
                "b": is_buy,                       # Buy side
                "p": str(price) if price else None,
                "s": str(quantity),               # Size
                "r": reduce_only,
                "t": {
                    "limit": {"tif": "Gtc"}
                } if order_type == OrderType.LIMIT else {"market": {}}
            }],
            "grouping": "na"
        }
        
        try:
            # POST to /exchange endpoint with signed action
            result = await self._request("POST", "/exchange", order_request)
            
            order_id = ""
            status = "rejected"
            
            if result.get("status") == "ok":
                status = "submitted"
                response = result.get("response", {})
                data = response.get("data", {})
                statuses = data.get("statuses", [])
                if statuses:
                    if "filled" in statuses[0]:
                        order_id = str(statuses[0]["filled"].get("oid", ""))
                        status = "filled"
                    elif "resting" in statuses[0]:
                        order_id = str(statuses[0]["resting"].get("oid", ""))
                        status = "open"
            
            return OrderResult(
                order_id=order_id,
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                status=status,
                raw_response=result
            )
        except Exception as e:
            return OrderResult(
                order_id="",
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                status="error",
                error=str(e)
            )
    
    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel order on HyperLiquid"""
        self._check_premium()
        
        try:
            cancel_request = {
                "type": "cancel",
                "cancels": [{
                    "a": symbol.replace("USDT", ""),
                    "o": int(order_id)
                }]
            }
            result = await self._request("POST", "/exchange", cancel_request)
            return result.get("status") == "ok"
        except Exception:
            return False
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get open orders from HyperLiquid"""
        self._check_premium()
        data = await self._request("POST", "/info", {
            "type": "openOrders",
            "user": self.credentials.wallet_address
        })
        return data if isinstance(data, list) else []
    
    async def set_leverage(self, symbol: str, leverage: int) -> bool:
        """Set leverage on HyperLiquid"""
        self._check_premium()
        # HyperLiquid leverage is set per-order
        return True
    
    async def get_ticker(self, symbol: str) -> Dict:
        """Get ticker from HyperLiquid"""
        self._check_premium()
        data = await self._request("POST", "/info", {"type": "allMids"})
        if isinstance(data, dict) and symbol in data:
            return {"symbol": symbol, "lastPrice": data[symbol]}
        return {}


class ExchangeService:
    """Factory and manager for exchange adapters"""
    
    def __init__(self):
        self._adapters: Dict[str, ExchangeAdapter] = {}
    
    def create_adapter(
        self,
        credentials: ExchangeCredentials,
        is_demo: bool = True,
        is_premium: bool = False
    ) -> ExchangeAdapter:
        """Create appropriate exchange adapter"""
        if credentials.exchange_type == ExchangeType.HYPERLIQUID:
            if not is_premium:
                raise PremiumRequiredError("HyperLiquid requires Premium license")
            adapter = HyperLiquidAdapter(credentials)
            adapter._is_premium_verified = True
        else:
            adapter = BybitAdapter(credentials, is_demo)
        
        return adapter
    
    async def get_adapter(
        self,
        user_id: int,
        exchange_type: ExchangeType,
        is_demo: bool = True
    ) -> ExchangeAdapter:
        """Get or create adapter for user"""
        key = f"{user_id}_{exchange_type.value}_{'demo' if is_demo else 'real'}"
        
        if key not in self._adapters:
            raise ExchangeNotConnectedError(f"No adapter for {exchange_type.value}")
        
        return self._adapters[key]
    
    def register_adapter(
        self,
        user_id: int,
        adapter: ExchangeAdapter,
        is_demo: bool = True
    ) -> None:
        """Register adapter for user"""
        key = f"{user_id}_{adapter.exchange_type.value}_{'demo' if is_demo else 'real'}"
        self._adapters[key] = adapter
    
    async def disconnect_all(self) -> None:
        """Disconnect all adapters"""
        for adapter in self._adapters.values():
            await adapter.disconnect()
        self._adapters.clear()


# Singleton instance
exchange_service = ExchangeService()
