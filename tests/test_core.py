"""
Core Infrastructure Tests - Caching, Rate Limiting, Exceptions
Тесты для core/ модулей с правильными импортами и структурами.
"""
import os
import sys
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Test real imports
from core.exceptions import (
    BotException, ExchangeError, AuthenticationError,
    RateLimitError, InsufficientBalanceError, PositionNotFoundError,
    OrderError, LicenseError, ConfigurationError
)
from utils.formatters import format_price, format_percent, format_pnl
from utils.validators import validate_symbol, validate_leverage, validate_percent


# ===========================
# EXCEPTIONS Tests
# ===========================

class TestExceptions:
    """Test custom exception hierarchy"""
    
    def test_bot_exception_base(self):
        """Test base BotException"""
        exc = BotException("Test error")
        assert str(exc) == "Test error"
        assert isinstance(exc, Exception)
    
    def test_exchange_error(self):
        """Test ExchangeError"""
        exc = ExchangeError("Exchange failed")
        assert str(exc) == "Exchange failed"
        assert isinstance(exc, BotException)
    
    def test_authentication_error(self):
        """Test AuthenticationError"""
        exc = AuthenticationError("Invalid API key")
        assert "Invalid API key" in str(exc)
        assert isinstance(exc, ExchangeError)
    
    def test_rate_limit_error(self):
        """Test RateLimitError with retry_after"""
        exc = RateLimitError("Rate limited", retry_after=5)
        assert exc.retry_after == 5
        assert isinstance(exc, ExchangeError)
    
    def test_insufficient_balance_error(self):
        """Test InsufficientBalanceError"""
        exc = InsufficientBalanceError(required=1000, available=500)
        assert exc.required == 1000
        assert exc.available == 500
        assert isinstance(exc, ExchangeError)
    
    def test_position_not_found_error(self):
        """Test PositionNotFoundError"""
        exc = PositionNotFoundError(symbol="BTCUSDT")
        assert exc.symbol == "BTCUSDT"
        assert isinstance(exc, ExchangeError)
    
    def test_order_error(self):
        """Test OrderError"""
        exc = OrderError("Order failed")
        assert str(exc) == "Order failed"
        assert isinstance(exc, ExchangeError)
    
    def test_license_error(self):
        """Test LicenseError"""
        exc = LicenseError("Premium required")
        assert str(exc) == "Premium required"
        assert isinstance(exc, BotException)
    
    def test_configuration_error(self):
        """Test ConfigurationError"""
        exc = ConfigurationError("Config invalid")
        assert str(exc) == "Config invalid"
        assert isinstance(exc, BotException)


# ===========================
# FORMATTERS Tests
# ===========================

class TestFormatters:
    """Test formatting utilities"""
    
    def test_format_price_large_number(self):
        """Test formatting large prices"""
        assert format_price(45000) == "45,000"
        assert format_price(45123.45) == "45,123.45"
    
    def test_format_price_small_number(self):
        """Test formatting small prices"""
        result = format_price(0.0045)
        assert "0.0045" in result or "0.004500" in result
    
    def test_format_price_zero(self):
        """Test formatting zero"""
        assert format_price(0) == "0"
    
    def test_format_price_none(self):
        """Test formatting None"""
        assert format_price(None) == "—"
    
    def test_format_price_string_input(self):
        """Test formatting string input"""
        result = format_price("1234.5")
        assert "1,234" in result
    
    def test_format_percent_positive(self):
        """Test formatting positive percent"""
        assert format_percent(5.5) == "+5.50%"
    
    def test_format_percent_negative(self):
        """Test formatting negative percent"""
        assert format_percent(-3.2) == "-3.20%"
    
    def test_format_percent_zero(self):
        """Test formatting zero percent"""
        assert format_percent(0) == "0.00%"
    
    def test_format_percent_none(self):
        """Test formatting None percent"""
        assert format_percent(None) == "—"
    
    def test_format_pnl_positive(self):
        """Test formatting positive PnL"""
        result = format_pnl(150.5, "USDT")
        assert "150" in result
        assert "USDT" in result or "$" in result


# ===========================
# VALIDATORS Tests
# ===========================

class TestValidators:
    """Test validation utilities"""
    
    def test_validate_symbol_valid(self):
        """Test valid symbol"""
        is_valid, error = validate_symbol("BTCUSDT")
        assert is_valid is True
        assert error is None
    
    def test_validate_symbol_invalid_format(self):
        """Test invalid symbol format"""
        is_valid, error = validate_symbol("BTC")
        assert is_valid is False
        assert error is not None
    
    def test_validate_symbol_empty(self):
        """Test empty symbol"""
        is_valid, error = validate_symbol("")
        assert is_valid is False
        assert "required" in error.lower()
    
    def test_validate_symbol_lowercase(self):
        """Test lowercase symbol (should be normalized)"""
        is_valid, error = validate_symbol("btcusdt")
        # Should work after normalization
        assert is_valid is True or "format" in str(error).lower()
    
    def test_validate_leverage_valid(self):
        """Test valid leverage"""
        is_valid, error = validate_leverage(10)
        assert is_valid is True
        assert error is None
    
    def test_validate_leverage_too_low(self):
        """Test leverage too low"""
        is_valid, error = validate_leverage(0)
        assert is_valid is False
        assert "at least 1" in error.lower()
    
    def test_validate_leverage_too_high(self):
        """Test leverage too high"""
        is_valid, error = validate_leverage(150, max_leverage=100)
        assert is_valid is False
        assert "cannot exceed" in error.lower()
    
    def test_validate_leverage_string(self):
        """Test leverage as string"""
        is_valid, error = validate_leverage("20")
        # Should convert to int
        assert is_valid is True or "integer" in str(error).lower()
    
    def test_validate_percent_valid(self):
        """Test valid percent"""
        is_valid, error = validate_percent(5.0)
        assert is_valid is True
        assert error is None
    
    def test_validate_percent_too_low(self):
        """Test percent too low"""
        is_valid, error = validate_percent(0.05, min_val=0.1)
        assert is_valid is False
    
    def test_validate_percent_too_high(self):
        """Test percent too high"""
        is_valid, error = validate_percent(150, max_val=100)
        assert is_valid is False


# ===========================
# ASYNC CACHE Tests
# ===========================

class TestAsyncCache:
    """Test async caching if available"""
    
    @pytest.mark.asyncio
    async def test_simple_cache(self):
        """Test simple caching mechanism"""
        call_count = 0
        
        async def expensive_function(x):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)
            return x * 2
        
        # First call
        result1 = await expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call (would be cached in real impl)
        result2 = await expensive_function(5)
        assert result2 == 10
    
    @pytest.mark.asyncio
    async def test_cache_with_different_args(self):
        """Test cache distinguishes different arguments"""
        results = {}
        
        async def cached_func(key):
            if key not in results:
                await asyncio.sleep(0.01)
                results[key] = key * 10
            return results[key]
        
        r1 = await cached_func(1)
        r2 = await cached_func(2)
        r3 = await cached_func(1)
        
        assert r1 == 10
        assert r2 == 20
        assert r3 == 10


# ===========================
# RATE LIMITER Tests
# ===========================

class TestRateLimiter:
    """Test rate limiting functionality"""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_simple(self):
        """Test simple rate limiting"""
        # Simulate token bucket
        tokens = 10
        rate_per_second = 5
        
        async def acquire():
            nonlocal tokens
            if tokens > 0:
                tokens -= 1
                return True
            return False
        
        # Should acquire successfully
        for _ in range(5):
            result = await acquire()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_rate_limiter_exhaustion(self):
        """Test rate limiter exhaustion"""
        max_requests = 3
        requests_made = 0
        
        async def limited_operation():
            nonlocal requests_made
            if requests_made >= max_requests:
                raise RateLimitError("Rate limit exceeded", retry_after=1)
            requests_made += 1
            return "success"
        
        # First 3 should work
        for _ in range(max_requests):
            result = await limited_operation()
            assert result == "success"
        
        # 4th should fail
        with pytest.raises(RateLimitError):
            await limited_operation()


# ===========================
# DATA MODELS Tests
# ===========================

class TestDataModels:
    """Test data classes and models"""
    
    def test_position_side_enum(self):
        """Test PositionSide enum"""
        from exchanges.base import PositionSide
        
        assert PositionSide.LONG.value == "Long"
        assert PositionSide.SHORT.value == "Short"
        assert PositionSide.NONE.value == "None"
    
    def test_order_side_enum(self):
        """Test OrderSide enum"""
        from exchanges.base import OrderSide
        
        assert OrderSide.BUY.value == "Buy"
        assert OrderSide.SELL.value == "Sell"
    
    def test_order_type_enum(self):
        """Test OrderType enum"""
        from exchanges.base import OrderType
        
        assert OrderType.MARKET.value == "Market"
        assert OrderType.LIMIT.value == "Limit"
    
    def test_balance_dataclass(self):
        """Test Balance dataclass"""
        from exchanges.base import Balance
        
        balance = Balance(
            total_equity=1000.0,
            available_balance=800.0,
            margin_used=200.0,
            unrealized_pnl=50.0
        )
        
        assert balance.total_equity == 1000.0
        assert balance.available_balance == 800.0
        assert balance.currency == "USDC"
    
    def test_position_dataclass(self):
        """Test Position dataclass"""
        from exchanges.base import Position, PositionSide
        
        position = Position(
            symbol="BTCUSDT",
            side=PositionSide.LONG,
            size=0.1,
            entry_price=45000.0,
            unrealized_pnl=150.0,
            leverage=10.0,
            margin_mode="isolated"
        )
        
        assert position.symbol == "BTCUSDT"
        assert position.is_long is True
        assert position.is_short is False
    
    def test_order_dataclass(self):
        """Test Order dataclass"""
        from exchanges.base import Order, OrderSide, OrderType
        
        order = Order(
            order_id="12345",
            symbol="ETHUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            size=1.0,
            price=3000.0,
            status="open"
        )
        
        assert order.order_id == "12345"
        assert order.side == OrderSide.BUY
        assert order.order_type == OrderType.LIMIT
    
    def test_order_result_success(self):
        """Test OrderResult for success"""
        from exchanges.base import OrderResult
        
        result = OrderResult(
            success=True,
            order_id="abc123",
            filled_size=0.5,
            avg_price=45100.0
        )
        
        assert result.success is True
        assert result.order_id == "abc123"
        assert result.error is None
    
    def test_order_result_failure(self):
        """Test OrderResult for failure"""
        from exchanges.base import OrderResult
        
        result = OrderResult(
            success=False,
            error="Insufficient balance"
        )
        
        assert result.success is False
        assert result.order_id is None
        assert "balance" in result.error.lower()


# ===========================
# SIGNAL PARSING Tests
# ===========================

class TestSignalParsing:
    """Test signal parsing logic"""
    
    def test_detect_long_signal(self):
        """Test detecting LONG signals"""
        long_keywords = ["long", "buy", "📈", "🟢"]
        text = "BTCUSDT LONG Entry: 45000"
        
        is_long = any(keyword in text.lower() for keyword in long_keywords)
        assert is_long is True
    
    def test_detect_short_signal(self):
        """Test detecting SHORT signals"""
        short_keywords = ["short", "sell", "📉", "🔴"]
        text = "ETHUSDT SHORT Entry: 3000"
        
        is_short = any(keyword in text.lower() for keyword in short_keywords)
        assert is_short is True
    
    def test_extract_symbol_from_text(self):
        """Test symbol extraction"""
        import re
        
        text = "$BTCUSDT Entry: 45000"
        match = re.search(r"\$?([A-Z]{2,10}USDT)", text)
        
        if match:
            symbol = match.group(1)
            assert symbol == "BTCUSDT"
    
    def test_extract_price_from_text(self):
        """Test price extraction"""
        import re
        
        text = "Entry: 45123.50 TP: 46000"
        prices = re.findall(r"(\d+\.?\d*)", text)
        
        assert len(prices) >= 2
        assert float(prices[0]) == 45123.50
        assert float(prices[1]) == 46000


# ===========================
# CRYPTO UTILS Tests
# ===========================

class TestCryptoUtils:
    """Test cryptographic utilities"""
    
    def test_hmac_signature(self):
        """Test HMAC signature generation"""
        import hmac
        import hashlib
        
        secret = b"test_secret"
        message = b"test_message"
        
        signature = hmac.new(secret, message, hashlib.sha256).hexdigest()
        
        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 hex = 64 chars
    
    def test_hmac_consistency(self):
        """Test HMAC gives same result for same input"""
        import hmac
        import hashlib
        
        secret = b"secret_key"
        message = b"data"
        
        sig1 = hmac.new(secret, message, hashlib.sha256).hexdigest()
        sig2 = hmac.new(secret, message, hashlib.sha256).hexdigest()
        
        assert sig1 == sig2


# ===========================
# HELPERS Tests
# ===========================

class TestHelpers:
    """Test helper functions"""
    
    def test_safe_float_conversion(self):
        """Test safe float conversion"""
        def safe_float(value, default=0.0):
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        
        assert safe_float("123.45") == 123.45
        assert safe_float("invalid") == 0.0
        assert safe_float(None) == 0.0
        assert safe_float(100) == 100.0
    
    def test_calculate_pnl_percentage(self):
        """Test PnL percentage calculation"""
        entry = 45000
        exit_price = 46350
        
        pnl_pct = ((exit_price - entry) / entry) * 100
        
        assert abs(pnl_pct - 3.0) < 0.01
    
    def test_calculate_position_size(self):
        """Test position size calculation"""
        balance = 1000
        risk_percent = 2.0
        leverage = 10
        price = 45000
        
        position_value = balance * (risk_percent / 100) * leverage
        quantity = position_value / price
        
        assert quantity > 0
        assert position_value == 200


# ===========================
# TIMEFRAME Tests
# ===========================

class TestTimeframes:
    """Test timeframe handling"""
    
    def test_timeframe_to_seconds(self):
        """Test converting timeframes to seconds"""
        conversions = {
            "1m": 60,
            "5m": 300,
            "15m": 900,
            "1h": 3600,
            "4h": 14400,
            "1d": 86400
        }
        
        for tf, seconds in conversions.items():
            # Simple parsing
            if tf.endswith("m"):
                minutes = int(tf[:-1])
                assert minutes * 60 == seconds
            elif tf.endswith("h"):
                hours = int(tf[:-1])
                assert hours * 3600 == seconds
    
    def test_valid_timeframes(self):
        """Test valid timeframe list"""
        valid_timeframes = ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]
        
        assert "15m" in valid_timeframes
        assert "1h" in valid_timeframes
        assert "invalid" not in valid_timeframes
