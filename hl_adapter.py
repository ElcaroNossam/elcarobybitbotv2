"""
HyperLiquid Adapter for Bot Compatibility
"""
import logging
import time
from typing import Dict, Any, Optional, List, Tuple

from hyperliquid import HyperLiquidClient, HyperLiquidError, coin_to_asset_id
from models import Position, Order, Balance, OrderResult, OrderSide, PositionSide

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# HYPERLIQUID ADAPTER CACHE - Prevent rate limiting (429 errors)
# HyperLiquid rate limit: 1200 weight/minute, info = 20 weight (~60 req/min)
# Cache responses for 120 seconds per wallet address
# ═══════════════════════════════════════════════════════════════
_hl_adapter_cache: Dict[str, Tuple[Any, float]] = {}  # key -> (data, timestamp)
HL_ADAPTER_CACHE_TTL = 120  # seconds - 2 minutes to avoid rate limits


def _get_adapter_cache(key: str) -> Optional[Any]:
    """Get cached HyperLiquid adapter data if not expired"""
    if key in _hl_adapter_cache:
        data, ts = _hl_adapter_cache[key]
        age = time.time() - ts
        if age < HL_ADAPTER_CACHE_TTL:
            # Reduced logging - only log cache hits rarely
            return data
    return None


def _set_adapter_cache(key: str, data: Any):
    """Set HyperLiquid adapter cache with current timestamp"""
    _hl_adapter_cache[key] = (data, time.time())
    # Reduced logging


def _safe_float(val, default=0.0):
    """Safely convert value to float, handling empty strings and None"""
    if val is None or val == '':
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


class HLAdapter:
    def __init__(self, private_key: str, testnet: bool = False, vault_address: Optional[str] = None, main_wallet_address: Optional[str] = None):
        """
        Initialize HLAdapter.
        
        Args:
            private_key: API wallet private key (for signing orders)
            testnet: Whether to use testnet
            vault_address: Vault address for trading on behalf of another wallet (auto-discovered if agent)
            main_wallet_address: Main wallet address for balance queries (auto-discovered if agent)
                                 If not set and wallet is an agent, will be auto-discovered
        """
        self._client = HyperLiquidClient(private_key=private_key, testnet=testnet, vault_address=vault_address)
        self._main_wallet_address = main_wallet_address
        self._initialized = False
        self._agent_checked = False

    @property
    def address(self) -> str:
        return self._client.address
    
    @property
    def main_wallet_address(self) -> str:
        """Returns main wallet address if set/discovered, otherwise API wallet address"""
        return self._main_wallet_address or self._client.main_wallet_address or self._client.address

    @property
    def is_testnet(self) -> bool:
        return self._client.is_testnet

    async def initialize(self):
        if not self._initialized:
            await self._client.initialize()
            self._initialized = True
        
        # Auto-discover main wallet if not set and not checked yet
        if not self._agent_checked and self._main_wallet_address is None:
            self._agent_checked = True
            discovered = await self._client.discover_main_wallet()
            if discovered:
                self._main_wallet_address = discovered
                logger.info(f"[HLAdapter] Auto-discovered main wallet: {discovered}")

    async def close(self):
        if self._client:
            try:
                await self._client.close()
            except Exception as e:
                logger.debug(f"Error closing HLAdapter client: {e}")
        self._initialized = False

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def fetch_positions(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch positions. Uses main_wallet_address if set.
        """
        await self.initialize()
        try:
            # Query positions from main wallet address if set
            query_address = self._main_wallet_address or self._client.address
            state = await self._client.user_state(address=query_address)
            asset_positions = state.get("assetPositions", [])
            
            result_list = []
            for p in asset_positions:
                pos = p.get("position", {})
                coin = pos.get("coin", "")
                if symbol and self._normalize_symbol(symbol) != coin:
                    continue
                size = _safe_float(pos.get("szi"))
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

    async def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get raw position list from HyperLiquid API.
        Returns list of position dicts with fields: coin, szi, entryPx, etc.
        Used for entry price lookup.
        """
        await self.initialize()
        try:
            query_address = self._main_wallet_address or self._client.address
            state = await self._client.user_state(address=query_address)
            asset_positions = state.get("assetPositions", [])
            
            result = []
            for p in asset_positions:
                pos = p.get("position", {})
                coin = pos.get("coin", "")
                if symbol:
                    # Normalize symbol for comparison (e.g., BTCUSDT -> BTC)
                    target_coin = self._normalize_symbol(symbol)
                    if target_coin != coin:
                        continue
                size = _safe_float(pos.get("szi"))
                if size == 0:
                    continue
                result.append({
                    "coin": coin,
                    "szi": pos.get("szi"),
                    "entryPx": pos.get("entryPx"),
                    "positionValue": pos.get("positionValue"),
                    "unrealizedPnl": pos.get("unrealizedPnl"),
                    "liquidationPx": pos.get("liquidationPx"),
                    "leverage": pos.get("leverage"),
                    "marginUsed": pos.get("marginUsed"),
                })
            return result
        except HyperLiquidError as e:
            logger.error(f"get_positions error: {e}")
            return []

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

    async def get_balance(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Detailed balance method for UI.
        Uses main_wallet_address if set (for API Wallet architecture where
        funds are on main wallet, not API wallet).
        
        Args:
            use_cache: Use cache to avoid rate limits (default True)
        """
        await self.initialize()
        
        # Query balance from main wallet address if set, otherwise from API wallet
        query_address = self._main_wallet_address or self._client.address
        
        # Check cache first to avoid rate limits
        if use_cache:
            network = "testnet" if self._client.is_testnet else "mainnet"
            cache_key = f"balance:{query_address}:{network}"
            cached = _get_adapter_cache(cache_key)
            if cached is not None:
                return cached
        
        try:
            state = await self._client.user_state(address=query_address)
            margin = state.get("marginSummary", {})
            
            perp_account_value = _safe_float(margin.get("accountValue"))
            perp_withdrawable = _safe_float(state.get("withdrawable"))
            
            # ═══════════════════════════════════════════════════════════════
            # UNIFIED ACCOUNT SUPPORT: If Perp balance is 0, check Spot
            # HyperLiquid Unified Account keeps funds in Spot, not Perp
            # ═══════════════════════════════════════════════════════════════
            spot_usdc_balance = 0.0
            is_unified_account = False
            
            if perp_account_value == 0:
                try:
                    spot_state = await self._client.spot_state(address=query_address)
                    spot_balances = spot_state.get("balances", [])
                    for bal in spot_balances:
                        if bal.get("coin") == "USDC":
                            spot_usdc_balance = _safe_float(bal.get("total", 0))
                            break
                    
                    # If Spot has USDC but Perp is 0, this is Unified Account
                    if spot_usdc_balance > 0:
                        is_unified_account = True
                        logger.info(f"[HL-UNIFIED] Detected Unified Account for {query_address}: Spot USDC={spot_usdc_balance}")
                except Exception as spot_err:
                    logger.debug(f"Error fetching Spot state: {spot_err}")
            
            # Use Spot balance if Unified Account detected
            effective_balance = spot_usdc_balance if is_unified_account else perp_account_value
            effective_available = spot_usdc_balance if is_unified_account else perp_withdrawable
            
            balance = {
                "account_value": effective_balance,
                "total_margin_used": _safe_float(margin.get("totalMarginUsed")),
                "total_ntl_pos": _safe_float(margin.get("totalNtlPos")),
                "withdrawable": effective_available,
            }
            
            # Get positions from main wallet
            positions = state.get("assetPositions", [])
            
            # Calculate metrics
            total_position_value = 0
            num_positions = 0
            pnl = 0
            for p in positions:
                pos = p.get("position", {})
                szi = _safe_float(pos.get("szi"))
                if szi != 0:
                    num_positions += 1
                    total_position_value += abs(_safe_float(pos.get("positionValue", 0)))
                    pnl += _safe_float(pos.get("unrealizedPnl", 0))
            
            result = {
                "success": True,
                "data": {
                    "equity": balance.get("account_value", 0),
                    "available": balance.get("withdrawable", 0),
                    "margin_used": balance.get("total_margin_used", 0),
                    "total_notional": balance.get("total_ntl_pos", 0),
                    "unrealized_pnl": pnl,
                    "position_value": total_position_value,
                    "num_positions": num_positions,
                    "currency": "USDC",  # HL uses USDC
                    "is_unified_account": is_unified_account,
                    "spot_usdc": spot_usdc_balance if is_unified_account else 0,
                }
            }
            
            # Cache the result
            if use_cache:
                network = "testnet" if self._client.is_testnet else "mainnet"
                cache_key = f"balance:{query_address}:{network}"
                _set_adapter_cache(cache_key, result)
            
            return result
        except Exception as e:
            logger.error(f"get_balance error: {e}")
            return {"success": False, "error": str(e)}

    async def get_spot_balance(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get SPOT balance (separate from Perp balance).
        Returns list of tokens with their balances.
        
        Args:
            use_cache: Use cache to avoid rate limits (default True)
        """
        await self.initialize()
        
        # Query balance from main wallet address if set, otherwise from API wallet
        query_address = self._main_wallet_address or self._client.address
        
        # Check cache first to avoid rate limits
        if use_cache:
            network = "testnet" if self._client.is_testnet else "mainnet"
            cache_key = f"spot_balance:{query_address}:{network}"
            cached = _get_adapter_cache(cache_key)
            if cached is not None:
                return cached
        
        try:
            spot_state = await self._client.spot_state(address=query_address)
            balances = spot_state.get("balances", [])
            
            tokens = []
            total_usdc_value = 0.0
            
            for bal in balances:
                token = bal.get("coin", "")
                total_str = bal.get("total", "0")
                hold_str = bal.get("hold", "0")
                entry_ntl_str = bal.get("entryNtl", "0")
                
                total_balance = _safe_float(total_str)
                hold_balance = _safe_float(hold_str)
                entry_ntl = _safe_float(entry_ntl_str)
                available = total_balance - hold_balance
                
                # Skip zero balances
                if total_balance == 0:
                    continue
                
                # Get USD value (entry_ntl for non-USDC, or total for USDC)
                if token == "USDC":
                    usd_value = total_balance
                else:
                    usd_value = entry_ntl if entry_ntl > 0 else total_balance
                
                total_usdc_value += usd_value
                
                tokens.append({
                    "token": token,
                    "total": total_balance,
                    "available": available,
                    "hold": hold_balance,
                    "usd_value": usd_value
                })
            
            result = {
                "success": True,
                "data": {
                    "tokens": tokens,
                    "total_usd_value": total_usdc_value,
                    "num_tokens": len(tokens)
                }
            }
            
            # Cache the result
            if use_cache:
                network = "testnet" if self._client.is_testnet else "mainnet"
                cache_key = f"spot_balance:{query_address}:{network}"
                _set_adapter_cache(cache_key, result)
            
            return result
        except Exception as e:
            logger.error(f"get_spot_balance error: {e}")
            return {"success": False, "error": str(e), "data": {"tokens": [], "total_usd_value": 0, "num_tokens": 0}}

    # ==================== SPOT TRADING ====================
    
    async def get_spot_pairs(self) -> Dict[str, Any]:
        """
        Get list of available spot trading pairs.
        
        Returns:
            Dict with success flag and list of pairs with asset_id, base_token, quote_token
        """
        await self.initialize()
        try:
            pairs = await self._client.get_spot_pairs()
            return {"success": True, "data": pairs}
        except Exception as e:
            logger.error(f"get_spot_pairs error: {e}")
            return {"success": False, "error": str(e), "data": []}
    
    async def get_spot_ticker(self, token: str) -> Dict[str, Any]:
        """
        Get spot ticker info for a token.
        
        Args:
            token: Token name (e.g., "PURR", "HYPE")
            
        Returns:
            Dict with success flag and ticker data
        """
        await self.initialize()
        try:
            ticker = await self._client.get_spot_ticker(token)
            if ticker:
                return {"success": True, "data": ticker}
            return {"success": False, "error": f"Token {token} not found", "data": None}
        except Exception as e:
            logger.error(f"get_spot_ticker error: {e}")
            return {"success": False, "error": str(e), "data": None}
    
    async def get_all_spot_tickers(self) -> Dict[str, Any]:
        """
        Get ticker info for all spot pairs.
        
        Returns:
            Dict with success flag and list of tickers
        """
        await self.initialize()
        try:
            tickers = await self._client.get_all_spot_tickers()
            return {"success": True, "data": tickers}
        except Exception as e:
            logger.error(f"get_all_spot_tickers error: {e}")
            return {"success": False, "error": str(e), "data": []}
    
    async def spot_market_buy(
        self,
        token: str,
        usdc_amount: float,
        slippage: float = 0.02
    ) -> Dict[str, Any]:
        """
        Buy a spot token with USDC (market order).
        
        Args:
            token: Token to buy (e.g., "PURR", "HYPE")
            usdc_amount: Amount of USDC to spend
            slippage: Slippage tolerance (default 2%)
            
        Returns:
            Dict with success flag and order result
        """
        await self.initialize()
        try:
            # Get current price to calculate qty
            ticker = await self._client.get_spot_ticker(token)
            if not ticker or ticker.get("price", 0) <= 0:
                return {"success": False, "error": f"Cannot get price for {token}"}
            
            price = ticker["price"]
            # Calculate qty from USDC amount
            qty = usdc_amount / price
            
            # Round qty appropriately (spot typically uses more decimals)
            qty = round(qty, 6)
            
            if qty <= 0:
                return {"success": False, "error": "Amount too small"}
            
            logger.info(f"[HL-SPOT] Buying {qty:.6f} {token} for ~${usdc_amount:.2f} USDC at price ~{price:.6f}")
            
            result = await self._client.spot_market_buy(
                base_token=token,
                sz=qty,
                slippage=slippage
            )
            
            # Extract order ID from response
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
            
            return {
                "success": result.get("status") == "ok",
                "order_id": order_id,
                "token": token,
                "qty": qty,
                "usdc_spent": usdc_amount,
                "price": price,
                "result": result
            }
        except Exception as e:
            logger.error(f"spot_market_buy error: {e}")
            return {"success": False, "error": str(e)}
    
    async def spot_market_sell(
        self,
        token: str,
        qty: float = None,
        sell_pct: float = None,
        slippage: float = 0.02
    ) -> Dict[str, Any]:
        """
        Sell a spot token for USDC (market order).
        
        Args:
            token: Token to sell (e.g., "PURR", "HYPE")
            qty: Quantity to sell. If None, use sell_pct.
            sell_pct: Percentage of holdings to sell (0-100). Used if qty is None.
            slippage: Slippage tolerance (default 2%)
            
        Returns:
            Dict with success flag and order result
        """
        await self.initialize()
        try:
            # If no qty specified, calculate from balance percentage
            if qty is None and sell_pct is not None:
                balance_result = await self.get_spot_balance()
                if not balance_result.get("success"):
                    return {"success": False, "error": "Failed to get balance"}
                
                token_balance = 0
                for t in balance_result.get("data", {}).get("tokens", []):
                    if t.get("token", "").upper() == token.upper():
                        token_balance = t.get("available", 0)
                        break
                
                if token_balance <= 0:
                    return {"success": False, "error": f"No {token} balance to sell"}
                
                qty = token_balance * (sell_pct / 100.0)
            
            if qty is None or qty <= 0:
                return {"success": False, "error": "Invalid quantity"}
            
            qty = round(qty, 6)
            
            # Get current price for logging
            ticker = await self._client.get_spot_ticker(token)
            price = ticker.get("price", 0) if ticker else 0
            
            logger.info(f"[HL-SPOT] Selling {qty:.6f} {token} at price ~{price:.6f}")
            
            result = await self._client.spot_market_sell(
                base_token=token,
                sz=qty,
                slippage=slippage
            )
            
            # Extract order ID from response
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
            
            return {
                "success": result.get("status") == "ok",
                "order_id": order_id,
                "token": token,
                "qty": qty,
                "usdc_received": qty * price if price else None,
                "price": price,
                "result": result
            }
        except Exception as e:
            logger.error(f"spot_market_sell error: {e}")
            return {"success": False, "error": str(e)}
    
    async def spot_transfer(
        self,
        usd_to_perp: bool,
        usd_amount: float
    ) -> Dict[str, Any]:
        """
        Transfer USDC between spot and perpetual accounts.
        
        Args:
            usd_to_perp: True to transfer SPOT→PERP, False for PERP→SPOT
            usd_amount: Amount of USDC to transfer
            
        Returns:
            Dict with success flag and result
        """
        await self.initialize()
        try:
            result = await self._client.spot_transfer(usd_to_perp=usd_to_perp, usd_amount=usd_amount)
            return {
                "success": result.get("status") == "ok",
                "direction": "SPOT→PERP" if usd_to_perp else "PERP→SPOT",
                "amount": usd_amount,
                "result": result
            }
        except Exception as e:
            logger.error(f"spot_transfer error: {e}")
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
                    "size": _safe_float(order.get("sz")),
                    "price": _safe_float(order.get("limitPx")),
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
            # HyperLiquid API for user fills - use main_wallet_address for Unified Account support
            fills = await self._client.user_fills(address=self._main_wallet_address)
            result_list = []
            for fill in fills[:limit]:
                result_list.append({
                    "symbol": f"{fill.get('coin', '')}USDC",
                    "side": "Buy" if fill.get("side") == "B" else "Sell",
                    "size": _safe_float(fill.get("sz")),
                    "price": _safe_float(fill.get("px")),
                    "pnl": _safe_float(fill.get("closedPnl")),
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
                    # Use main_wallet_address for Unified Account support
                    await self._client.set_tp_sl(coin=coin, tp_price=take_profit, sl_price=stop_loss, address=self._main_wallet_address)
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

    async def set_leverage(self, symbol: str, leverage: int, margin_mode: str = "cross") -> Dict[str, Any]:
        """
        Set leverage for a symbol.
        margin_mode: "cross" or "isolated"
        """
        await self.initialize()
        coin = self._normalize_symbol(symbol)
        is_cross = margin_mode.lower() != "isolated"
        try:
            result = await self._client.update_leverage(coin=coin, leverage=leverage, is_cross=is_cross)
            return {"retCode": 0 if result.get("status") == "ok" else 1, "retMsg": "OK" if result.get("status") == "ok" else str(result), "result": {}}
        except HyperLiquidError as e:
            logger.error(f"set_leverage error: {e}")
            return {"retCode": 1, "retMsg": str(e), "result": {}}

    async def set_stop_loss(self, symbol: str, stop_loss_price: float, qty: Optional[float] = None) -> Dict[str, Any]:
        await self.initialize()
        coin = self._normalize_symbol(symbol)
        try:
            # Pass main_wallet_address for Unified Account - positions are on main wallet
            results = await self._client.set_tp_sl(coin=coin, sl_price=stop_loss_price, sz=qty, address=self._main_wallet_address)
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
            # Pass main_wallet_address for Unified Account - positions are on main wallet
            results = await self._client.set_tp_sl(coin=coin, tp_price=take_profit_price, sz=qty, address=self._main_wallet_address)
            for r in results:
                if r.get("type") == "tp":
                    result = r.get("result", {})
                    return {"retCode": 0 if result.get("status") == "ok" else 1, "retMsg": "OK" if result.get("status") == "ok" else str(result), "result": {}}
            return {"retCode": 1, "retMsg": "TP not set", "result": {}}
        except HyperLiquidError as e:
            logger.error(f"set_take_profit error: {e}")
            return {"retCode": 1, "retMsg": str(e), "result": {}}

    async def set_tp_sl(self, coin: str, tp_price: Optional[float] = None, sl_price: Optional[float] = None, sz: Optional[float] = None, address: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Set TP/SL for a position.
        This method is a direct wrapper for the underlying client's set_tp_sl.
        
        Args:
            coin: Trading coin (e.g., 'BTC')
            tp_price: Take profit price (optional)
            sl_price: Stop loss price (optional)
            sz: Size (optional, uses full position if not specified)
            address: Main wallet address (CRITICAL for Unified Account!)
                     If None, uses self._main_wallet_address
        
        Returns:
            List of result dicts with 'type': 'tp' or 'sl' and 'result': {...}
        """
        await self.initialize()
        coin = self._normalize_symbol(coin)
        # Use main_wallet_address if not specified - CRITICAL for Unified Account
        wallet_address = address or self._main_wallet_address
        try:
            return await self._client.set_tp_sl(
                coin=coin,
                tp_price=tp_price,
                sl_price=sl_price,
                sz=sz,
                address=wallet_address
            )
        except HyperLiquidError as e:
            logger.error(f"set_tp_sl error: {e}")
            return []

    async def close_position(self, symbol: str, qty: Optional[float] = None) -> Dict[str, Any]:
        await self.initialize()
        coin = self._normalize_symbol(symbol)
        try:
            # Pass main_wallet_address for Unified Account - positions are on main wallet
            result = await self._client.market_close(coin=coin, sz=qty, address=self._main_wallet_address)
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
                    "open": _safe_float(c.get("o")),
                    "high": _safe_float(c.get("h")),
                    "low": _safe_float(c.get("l")),
                    "close": _safe_float(c.get("c")),
                    "volume": _safe_float(c.get("v")),
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
                    "size": _safe_float(fill.get("sz")),
                    "price": _safe_float(fill.get("px")),
                    "pnl": _safe_float(fill.get("closedPnl")),
                    "fee": _safe_float(fill.get("fee")),
                    "time": fill.get("time", 0),
                    "hash": fill.get("hash", ""),
                    "direction": fill.get("dir", ""),
                })
            return {"success": True, "data": result_list}
        except Exception as e:
            logger.error(f"get_fills_by_time error: {e}")
            return {"success": False, "error": str(e)}

    # ═══════════════════════════════════════════════════════════════
    # SPOT TRADING METHODS
    # ═══════════════════════════════════════════════════════════════

    async def get_spot_balances(self) -> Dict[str, Any]:
        """
        Get spot token balances for the main wallet.
        
        Returns:
            Dict with balances: {token: {"total": float, "hold": float, "available": float}}
        """
        await self.initialize()
        try:
            query_address = self._main_wallet_address or self._client.vault_address or self._client.address
            spot_state = await self._client.spot_state(address=query_address)
            
            balances = {}
            for bal in spot_state.get("balances", []):
                coin = bal.get("coin", "")
                total = _safe_float(bal.get("total", 0))
                hold = _safe_float(bal.get("hold", 0))
                if total > 0 or hold > 0:  # Only include non-zero balances
                    balances[coin] = {
                        "total": total,
                        "hold": hold,
                        "available": total - hold
                    }
            return {"success": True, "balances": balances}
        except Exception as e:
            logger.error(f"get_spot_balances error: {e}")
            return {"success": False, "error": str(e), "balances": {}}

    async def spot_buy(
        self,
        token: str,
        size: float,
        slippage: float = 0.05
    ) -> Dict[str, Any]:
        """
        Place a spot market buy order.
        
        Args:
            token: Token to buy (e.g., "PURR", "HYPE")
            size: Size in base token (must be integer for tokens with szDecimals=0)
            slippage: Slippage tolerance (default 5%)
            
        Returns:
            Order result dict
        """
        await self.initialize()
        try:
            result = await self._client.spot_market_buy(
                base_token=token.upper(),
                sz=size,
                slippage=slippage
            )
            
            statuses = result.get("response", {}).get("data", {}).get("statuses", [])
            if statuses:
                status = statuses[0]
                if isinstance(status, dict):
                    if status.get("error"):
                        return {"success": False, "error": status["error"]}
                    if status.get("filled"):
                        filled = status["filled"]
                        return {
                            "success": True,
                            "filled": True,
                            "size": _safe_float(filled.get("totalSz")),
                            "avg_price": _safe_float(filled.get("avgPx")),
                            "order_id": filled.get("oid"),
                        }
            
            return {"success": True, "result": result}
        except HyperLiquidError as e:
            logger.error(f"spot_buy error: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.exception(f"spot_buy unexpected error: {e}")
            return {"success": False, "error": str(e)}

    async def spot_sell(
        self,
        token: str,
        size: float,
        slippage: float = 0.05
    ) -> Dict[str, Any]:
        """
        Place a spot market sell order.
        
        Args:
            token: Token to sell (e.g., "PURR", "HYPE")
            size: Size in base token (must be integer for tokens with szDecimals=0)
            slippage: Slippage tolerance (default 5%)
            
        Returns:
            Order result dict
        """
        await self.initialize()
        try:
            result = await self._client.spot_market_sell(
                base_token=token.upper(),
                sz=size,
                slippage=slippage
            )
            
            statuses = result.get("response", {}).get("data", {}).get("statuses", [])
            if statuses:
                status = statuses[0]
                if isinstance(status, dict):
                    if status.get("error"):
                        return {"success": False, "error": status["error"]}
                    if status.get("filled"):
                        filled = status["filled"]
                        return {
                            "success": True,
                            "filled": True,
                            "size": _safe_float(filled.get("totalSz")),
                            "avg_price": _safe_float(filled.get("avgPx")),
                            "order_id": filled.get("oid"),
                        }
            
            return {"success": True, "result": result}
        except HyperLiquidError as e:
            logger.error(f"spot_sell error: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.exception(f"spot_sell unexpected error: {e}")
            return {"success": False, "error": str(e)}

    async def get_spot_ticker(self, token: str) -> Dict[str, Any]:
        """
        Get spot ticker info for a token.
        
        Args:
            token: Token name (e.g., "PURR", "HYPE")
            
        Returns:
            Dict with price, volume, etc.
        """
        await self.initialize()
        try:
            ticker = await self._client.get_spot_ticker(token.upper())
            if ticker:
                return {
                    "success": True,
                    "symbol": f"{token.upper()}/USDC",
                    "mid_price": ticker.get("midPx"),
                    "mark_price": ticker.get("markPx"),
                    "day_volume": ticker.get("dayNtlVlm"),
                    "prev_day_price": ticker.get("prevDayPx"),
                }
            return {"success": False, "error": "Token not found"}
        except Exception as e:
            logger.error(f"get_spot_ticker error: {e}")
            return {"success": False, "error": str(e)}

    async def get_spot_markets(self) -> List[Dict[str, Any]]:
        """
        Get list of available spot markets.
        
        Returns:
            List of spot market info dicts
        """
        await self.initialize()
        try:
            spot_data = await self._client.spot_meta_and_asset_contexts()
            if len(spot_data) < 2:
                return []
            
            spot_meta = spot_data[0]
            spot_ctxs = spot_data[1]
            universe = spot_meta.get("universe", [])
            tokens = spot_meta.get("tokens", [])
            
            markets = []
            for idx, pair in enumerate(universe):
                token_indices = pair.get("tokens", [])
                base_idx = token_indices[0] if len(token_indices) > 0 else None
                quote_idx = token_indices[1] if len(token_indices) > 1 else None
                
                base_name = tokens[base_idx].get("name") if base_idx is not None and base_idx < len(tokens) else "?"
                quote_name = tokens[quote_idx].get("name") if quote_idx is not None and quote_idx < len(tokens) else "USDC"
                sz_decimals = tokens[base_idx].get("szDecimals", 0) if base_idx is not None else 0
                
                mid_price = None
                if idx < len(spot_ctxs):
                    mid_price = _safe_float(spot_ctxs[idx].get("midPx"))
                
                markets.append({
                    "symbol": f"{base_name}/{quote_name}",
                    "base": base_name,
                    "quote": quote_name,
                    "pair_index": idx,
                    "sz_decimals": sz_decimals,
                    "mid_price": mid_price,
                })
            
            return markets
        except Exception as e:
            logger.error(f"get_spot_markets error: {e}")
            return []


async def create_hl_adapter(
    private_key: str, 
    testnet: bool = False, 
    vault_address: Optional[str] = None,
    main_wallet_address: Optional[str] = None
) -> HLAdapter:
    """
    Create and initialize HLAdapter.
    
    Args:
        private_key: API wallet private key (for signing orders)
        testnet: Whether to use testnet
        vault_address: Vault address for trading on behalf of another wallet (requires agent registration)
        main_wallet_address: Main wallet address for balance/position queries (for API Wallet architecture)
    """
    adapter = HLAdapter(
        private_key=private_key, 
        testnet=testnet, 
        vault_address=vault_address,
        main_wallet_address=main_wallet_address
    )
    await adapter.initialize()
    return adapter
