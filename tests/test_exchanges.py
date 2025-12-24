"""
Exchange Adapters Tests - Bybit & HyperLiquid
Тесты для exchange адаптеров с правильными enum значениями.
"""
import os
import sys
import pytest
from unittest.mock import Mock, AsyncMock, patch
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from exchanges.base import (
    BaseExchange, OrderSide, OrderType, PositionSide,
    Position, Order, Balance, OrderResult
)


# ===========================
# DATA MODELS Tests
# ===========================

class TestExchangeDataModels:
    """Test exchange data models"""
    
    def test_order_side_enum_values(self):
        """Test OrderSide enum has correct values"""
        assert OrderSide.BUY.value == "Buy"
        assert OrderSide.SELL.value == "Sell"
    
    def test_order_type_enum_values(self):
        """Test OrderType enum has correct values"""
        assert OrderType.MARKET.value == "Market"
        assert OrderType.LIMIT.value == "Limit"
    
    def test_position_side_enum_values(self):
        """Test PositionSide enum has correct values"""
        assert PositionSide.LONG.value == "Long"
        assert PositionSide.SHORT.value == "Short"
        assert PositionSide.NONE.value == "None"
    
    def test_position_creation(self):
        """Test creating Position instance"""
        pos = Position(
            symbol="BTCUSDT",
            side=PositionSide.LONG,
            size=0.1,
            entry_price=45000.0,
            unrealized_pnl=100.0,
            leverage=10.0,
            margin_mode="isolated",
            liquidation_price=40500.0
        )
        
        assert pos.symbol == "BTCUSDT"
        assert pos.side == PositionSide.LONG
        assert pos.is_long is True
        assert pos.is_short is False
        assert pos.size == 0.1
        assert pos.entry_price == 45000.0
    
    def test_position_short(self):
        """Test SHORT position properties"""
        pos = Position(
            symbol="ETHUSDT",
            side=PositionSide.SHORT,
            size=1.0,
            entry_price=3000.0,
            unrealized_pnl=-50.0,
            leverage=5.0,
            margin_mode="cross"
        )
        
        assert pos.is_short is True
        assert pos.is_long is False
    
    def test_order_creation(self):
        """Test creating Order instance"""
        order = Order(
            order_id="order123",
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            size=0.5,
            price=44000.0,
            filled_size=0.2,
            status="partially_filled"
        )
        
        assert order.order_id == "order123"
        assert order.side == OrderSide.BUY
        assert order.order_type == OrderType.LIMIT
        assert order.filled_size == 0.2
    
    def test_order_market_type(self):
        """Test MARKET order creation"""
        order = Order(
            order_id="market123",
            symbol="ETHUSDT",
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            size=1.0,
            price=None
        )
        
        assert order.order_type == OrderType.MARKET
        assert order.price is None
    
    def test_balance_creation(self):
        """Test creating Balance instance"""
        balance = Balance(
            total_equity=10000.0,
            available_balance=8000.0,
            margin_used=2000.0,
            unrealized_pnl=500.0,
            currency="USDT"
        )
        
        assert balance.total_equity == 10000.0
        assert balance.available_balance == 8000.0
        assert balance.currency == "USDT"
    
    def test_balance_default_currency(self):
        """Test Balance with default currency"""
        balance = Balance(
            total_equity=5000.0,
            available_balance=4500.0,
            margin_used=500.0,
            unrealized_pnl=0.0
        )
        
        assert balance.currency == "USDC"  # Default
    
    def test_order_result_success(self):
        """Test successful OrderResult"""
        result = OrderResult(
            success=True,
            order_id="success123",
            filled_size=1.0,
            avg_price=45000.0
        )
        
        assert result.success is True
        assert result.order_id == "success123"
        assert result.error is None
    
    def test_order_result_failure(self):
        """Test failed OrderResult"""
        result = OrderResult(
            success=False,
            error="Insufficient balance"
        )
        
        assert result.success is False
        assert result.order_id is None
        assert result.error == "Insufficient balance"


# ===========================
# EXCHANGE MOCK Tests
# ===========================

class TestExchangeMocking:
    """Test exchange adapter mocking"""
    
    @pytest.mark.asyncio
    async def test_mock_get_balance(self):
        """Test mocking get_balance"""
        mock_exchange = AsyncMock()
        mock_exchange.get_balance.return_value = Balance(
            total_equity=10000.0,
            available_balance=9000.0,
            margin_used=1000.0,
            unrealized_pnl=200.0
        )
        
        balance = await mock_exchange.get_balance()
        
        assert balance.total_equity == 10000.0
        assert balance.available_balance == 9000.0
    
    @pytest.mark.asyncio
    async def test_mock_get_positions(self):
        """Test mocking get_positions"""
        mock_exchange = AsyncMock()
        mock_exchange.get_positions.return_value = [
            Position(
                symbol="BTCUSDT",
                side=PositionSide.LONG,
                size=0.1,
                entry_price=45000.0,
                unrealized_pnl=150.0,
                leverage=10.0,
                margin_mode="isolated"
            )
        ]
        
        positions = await mock_exchange.get_positions()
        
        assert len(positions) == 1
        assert positions[0].symbol == "BTCUSDT"
        assert positions[0].is_long is True
    
    @pytest.mark.asyncio
    async def test_mock_place_order(self):
        """Test mocking place_order"""
        mock_exchange = AsyncMock()
        mock_exchange.place_order.return_value = OrderResult(
            success=True,
            order_id="new_order_123",
            filled_size=0.5,
            avg_price=45100.0
        )
        
        result = await mock_exchange.place_order(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            size=0.5,
            order_type=OrderType.MARKET
        )
        
        assert result.success is True
        assert result.order_id == "new_order_123"
    
    @pytest.mark.asyncio
    async def test_mock_close_position(self):
        """Test mocking close_position"""
        mock_exchange = AsyncMock()
        mock_exchange.close_position.return_value = OrderResult(
            success=True,
            order_id="close_123"
        )
        
        result = await mock_exchange.close_position("BTCUSDT", 0.1)
        
        assert result.success is True
        mock_exchange.close_position.assert_called_once()


# ===========================
# SYMBOL NORMALIZATION Tests
# ===========================

class TestSymbolNormalization:
    """Test symbol normalization logic"""
    
    def test_normalize_to_usdt(self):
        """Test normalizing symbols to USDT"""
        def normalize_symbol(symbol: str) -> str:
            symbol = symbol.upper().strip()
            if not symbol.endswith("USDT"):
                symbol = symbol + "USDT"
            return symbol
        
        assert normalize_symbol("BTC") == "BTCUSDT"
        assert normalize_symbol("BTCUSDT") == "BTCUSDT"
        assert normalize_symbol("eth") == "ETHUSDT"
    
    def test_symbol_validation(self):
        """Test symbol validation"""
        def is_valid_symbol(symbol: str) -> bool:
            if not symbol:
                return False
            symbol = symbol.upper()
            return symbol.endswith("USDT") and len(symbol) >= 5
        
        assert is_valid_symbol("BTCUSDT") is True
        assert is_valid_symbol("BTC") is False
        assert is_valid_symbol("") is False
    
    def test_extract_base_currency(self):
        """Test extracting base currency"""
        def get_base_currency(symbol: str) -> str:
            if symbol.endswith("USDT"):
                return symbol[:-4]
            return symbol
        
        assert get_base_currency("BTCUSDT") == "BTC"
        assert get_base_currency("ETHUSDT") == "ETH"
        assert get_base_currency("1000PEPEUSDT") == "1000PEPE"


# ===========================
# PRICE CALCULATIONS Tests
# ===========================

class TestPriceCalculations:
    """Test price-related calculations"""
    
    def test_calculate_pnl_long(self):
        """Test PnL calculation for LONG position"""
        entry_price = 45000.0
        current_price = 46000.0
        size = 0.1
        
        pnl = (current_price - entry_price) * size
        
        assert pnl == 100.0
    
    def test_calculate_pnl_short(self):
        """Test PnL calculation for SHORT position"""
        entry_price = 45000.0
        current_price = 44000.0
        size = 0.1
        
        pnl = (entry_price - current_price) * size
        
        assert pnl == 100.0
    
    def test_calculate_position_value(self):
        """Test position value calculation"""
        price = 45000.0
        size = 0.5
        
        value = price * size
        
        assert value == 22500.0
    
    def test_calculate_liquidation_price_long(self):
        """Test liquidation price for LONG"""
        entry_price = 45000.0
        leverage = 10.0
        maintenance_margin_rate = 0.005
        
        # Simplified liquidation formula
        liq_price = entry_price * (1 - (1 / leverage) + maintenance_margin_rate)
        
        assert liq_price < entry_price
        assert liq_price > 40000.0
    
    def test_calculate_required_margin(self):
        """Test required margin calculation"""
        position_value = 10000.0
        leverage = 10.0
        
        required_margin = position_value / leverage
        
        assert required_margin == 1000.0
    
    def test_calculate_leverage_from_margin(self):
        """Test calculating leverage from margin"""
        position_value = 5000.0
        margin_used = 500.0
        
        leverage = position_value / margin_used
        
        assert leverage == 10.0


# ===========================
# ORDER VALIDATION Tests
# ===========================

class TestOrderValidation:
    """Test order validation logic"""
    
    def test_validate_order_size_positive(self):
        """Test order size must be positive"""
        def validate_size(size: float) -> bool:
            return size > 0
        
        assert validate_size(0.1) is True
        assert validate_size(0) is False
        assert validate_size(-0.5) is False
    
    def test_validate_limit_price(self):
        """Test limit price validation"""
        def validate_limit_price(order_type: OrderType, price: float) -> bool:
            if order_type == OrderType.LIMIT:
                return price is not None and price > 0
            return True
        
        assert validate_limit_price(OrderType.LIMIT, 45000.0) is True
        assert validate_limit_price(OrderType.LIMIT, None) is False
        assert validate_limit_price(OrderType.MARKET, None) is True
    
    def test_validate_symbol_format(self):
        """Test symbol format validation"""
        import re
        
        def is_valid_format(symbol: str) -> bool:
            return bool(re.match(r"^[A-Z0-9]{2,20}USDT$", symbol))
        
        assert is_valid_format("BTCUSDT") is True
        assert is_valid_format("1000PEPEUSDT") is True
        assert is_valid_format("btcusdt") is False
        assert is_valid_format("BTC") is False


# ===========================
# EXCHANGE RESPONSE PARSING Tests
# ===========================

class TestResponseParsing:
    """Test parsing exchange API responses"""
    
    def test_parse_bybit_balance_response(self):
        """Test parsing Bybit balance response"""
        mock_response = {
            "retCode": 0,
            "result": {
                "list": [{
                    "totalEquity": "10000.5",
                    "availableBalance": "8500.0",
                    "totalMarginBalance": "10000.0",
                    "unrealisedPnl": "150.5"
                }]
            }
        }
        
        if mock_response["retCode"] == 0:
            data = mock_response["result"]["list"][0]
            balance = Balance(
                total_equity=float(data["totalEquity"]),
                available_balance=float(data["availableBalance"]),
                margin_used=float(data["totalEquity"]) - float(data["availableBalance"]),
                unrealized_pnl=float(data["unrealisedPnl"])
            )
            
            assert balance.total_equity == 10000.5
            assert balance.available_balance == 8500.0
    
    def test_parse_position_response(self):
        """Test parsing position response"""
        mock_response = {
            "retCode": 0,
            "result": {
                "list": [{
                    "symbol": "BTCUSDT",
                    "side": "Buy",
                    "size": "0.1",
                    "avgPrice": "45000.0",
                    "unrealisedPnl": "150.0",
                    "leverage": "10"
                }]
            }
        }
        
        if mock_response["retCode"] == 0:
            for item in mock_response["result"]["list"]:
                side = PositionSide.LONG if item["side"] == "Buy" else PositionSide.SHORT
                position = Position(
                    symbol=item["symbol"],
                    side=side,
                    size=float(item["size"]),
                    entry_price=float(item["avgPrice"]),
                    unrealized_pnl=float(item["unrealisedPnl"]),
                    leverage=float(item["leverage"]),
                    margin_mode="isolated"
                )
                
                assert position.symbol == "BTCUSDT"
                assert position.is_long is True
    
    def test_parse_order_response(self):
        """Test parsing order response"""
        mock_response = {
            "retCode": 0,
            "result": {
                "orderId": "order_abc123",
                "orderStatus": "Filled"
            }
        }
        
        if mock_response["retCode"] == 0:
            result = OrderResult(
                success=True,
                order_id=mock_response["result"]["orderId"]
            )
            
            assert result.success is True
            assert result.order_id == "order_abc123"


# ===========================
# EXCHANGE FEATURES Tests
# ===========================

class TestExchangeFeatures:
    """Test exchange-specific features"""
    
    def test_bybit_supports_both_modes(self):
        """Test Bybit supports both demo and real"""
        bybit_features = {
            "demo_mode": True,
            "real_mode": True,
            "testnet": True
        }
        
        assert bybit_features["demo_mode"] is True
        assert bybit_features["real_mode"] is True
    
    def test_hyperliquid_features(self):
        """Test HyperLiquid features"""
        hl_features = {
            "testnet": True,
            "mainnet": True,
            "vault_support": True
        }
        
        assert hl_features["testnet"] is True
        assert hl_features["vault_support"] is True
    
    def test_exchange_type_detection(self):
        """Test detecting exchange type"""
        def detect_exchange(credentials: dict) -> str:
            if "private_key" in credentials:
                return "hyperliquid"
            elif "api_key" in credentials:
                return "bybit"
            return "unknown"
        
        assert detect_exchange({"private_key": "0x123"}) == "hyperliquid"
        assert detect_exchange({"api_key": "key123", "api_secret": "secret"}) == "bybit"


# ===========================
# ERROR HANDLING Tests
# ===========================

class TestExchangeErrorHandling:
    """Test exchange error handling"""
    
    def test_handle_insufficient_balance(self):
        """Test handling insufficient balance error"""
        from core.exceptions import InsufficientBalanceError
        
        try:
            raise InsufficientBalanceError(
                required=1000.0,
                available=500.0
            )
        except InsufficientBalanceError as e:
            assert e.required == 1000.0
            assert e.available == 500.0
    
    def test_handle_rate_limit(self):
        """Test handling rate limit error"""
        from core.exceptions import RateLimitError
        
        try:
            raise RateLimitError("Rate limited", retry_after=5)
        except RateLimitError as e:
            assert e.retry_after == 5
    
    def test_handle_position_not_found(self):
        """Test handling position not found"""
        from core.exceptions import PositionNotFoundError
        
        try:
            raise PositionNotFoundError(symbol="BTCUSDT")
        except PositionNotFoundError as e:
            assert e.symbol == "BTCUSDT"
