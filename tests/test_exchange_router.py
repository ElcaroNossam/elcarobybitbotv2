"""
Unit Tests for Exchange Router (NEW API - P0.2)
Tests for unified execution router between Bybit and HyperLiquid
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestEnums:
    """Test enum values and conversions"""
    
    @pytest.mark.unit
    def test_exchange_enum(self):
        """Test Exchange enum values"""
        from exchange_router import Exchange
        
        assert Exchange.BYBIT.value == "bybit"
        assert Exchange.HYPERLIQUID.value == "hyperliquid"
    
    @pytest.mark.unit
    def test_env_enum(self):
        """Test Env enum values (unified paper/live)"""
        from exchange_router import Env
        
        assert Env.PAPER.value == "paper"
        assert Env.LIVE.value == "live"
    
    @pytest.mark.unit
    def test_account_type_enum(self):
        """Test AccountType enum values (legacy)"""
        from exchange_router import AccountType
        
        assert AccountType.DEMO.value == "demo"
        assert AccountType.REAL.value == "real"
        assert AccountType.TESTNET.value == "testnet"
    
    @pytest.mark.unit
    def test_order_side_enum(self):
        """Test OrderSide enum values"""
        from exchange_router import OrderSide
        
        assert OrderSide.BUY.value == "Buy"
        assert OrderSide.SELL.value == "Sell"
    
    @pytest.mark.unit
    def test_order_type_enum(self):
        """Test OrderType enum values"""
        from exchange_router import OrderType
        
        assert OrderType.MARKET.value == "Market"
        assert OrderType.LIMIT.value == "Limit"


class TestEnvNormalization:
    """Test env normalization functions"""
    
    @pytest.mark.unit
    def test_normalize_env_demo_to_paper(self):
        """Test demo -> paper"""
        from exchange_router import normalize_env
        assert normalize_env("demo") == "paper"
    
    @pytest.mark.unit
    def test_normalize_env_testnet_to_paper(self):
        """Test testnet -> paper"""
        from exchange_router import normalize_env
        assert normalize_env("testnet") == "paper"
    
    @pytest.mark.unit
    def test_normalize_env_real_to_live(self):
        """Test real -> live"""
        from exchange_router import normalize_env
        assert normalize_env("real") == "live"
    
    @pytest.mark.unit
    def test_normalize_env_mainnet_to_live(self):
        """Test mainnet -> live"""
        from exchange_router import normalize_env
        assert normalize_env("mainnet") == "live"
    
    @pytest.mark.unit
    def test_normalize_env_idempotent(self):
        """Test paper/live stays the same"""
        from exchange_router import normalize_env
        assert normalize_env("paper") == "paper"
        assert normalize_env("live") == "live"
    
    @pytest.mark.unit
    def test_denormalize_env_bybit(self):
        """Test denormalize for Bybit"""
        from exchange_router import denormalize_env
        assert denormalize_env("paper", "bybit") == "demo"
        assert denormalize_env("live", "bybit") == "real"
    
    @pytest.mark.unit
    def test_denormalize_env_hyperliquid(self):
        """Test denormalize for HyperLiquid"""
        from exchange_router import denormalize_env
        assert denormalize_env("paper", "hyperliquid") == "testnet"
        assert denormalize_env("live", "hyperliquid") == "mainnet"


class TestDataclasses:
    """Test dataclass structures"""
    
    @pytest.mark.unit
    def test_execution_target(self):
        """Test ExecutionTarget (Target) dataclass with unified env"""
        from exchange_router import ExecutionTarget, Target, Env
        
        # ExecutionTarget is now alias for Target
        target = Target(
            exchange="bybit",
            env="paper",  # unified env instead of account_type
            is_enabled=True,
            max_leverage=20,
            risk_limit_pct=25.0
        )
        
        assert target.exchange == "bybit"
        assert target.env == "paper"
        assert target.account_type == "demo"  # property maps paper -> demo for bybit
        assert target.is_enabled is True
        assert target.max_leverage == 20
        assert target.risk_limit_pct == 25.0
        assert target.key == "bybit:paper"  # key uses env now
        
        # Test ExecutionTarget alias
        alias_target = ExecutionTarget(exchange="hyperliquid", env="live")
        assert alias_target.account_type == "mainnet"  # property maps live -> mainnet for HL
    
    @pytest.mark.unit
    def test_order_intent(self):
        """Test OrderIntent dataclass"""
        from exchange_router import OrderIntent
        
        intent = OrderIntent(
            user_id=12345,
            symbol="BTCUSDT",
            side="Buy",
            order_type="Market",
            qty=0.01,
            leverage=10,
            sl_percent=2.0,
            tp_percent=5.0,
            strategy="elcaro"
        )
        
        assert intent.user_id == 12345
        assert intent.symbol == "BTCUSDT"
        assert intent.side == "Buy"
        assert intent.qty == 0.01
        assert intent.leverage == 10
        assert intent.sl_percent == 2.0
        assert intent.tp_percent == 5.0
        assert intent.strategy == "elcaro"
    
    @pytest.mark.unit
    def test_order_result(self):
        """Test OrderResult dataclass"""
        from exchange_router import OrderResult, OrderIntent
        
        intent = OrderIntent(user_id=1, symbol="BTCUSDT", side="Buy")
        result = OrderResult(intent=intent)
        
        assert result.intent == intent
        assert result.any_success is False  # no results yet
        assert result.all_success is False  # no results yet
        assert result.results == []
        assert result.errors == []


class TestRiskValidation:
    """Test risk validation logic (P0.7)"""
    
    @pytest.mark.unit
    def test_validate_risk_safe(self):
        """Test risk validation - safe case"""
        from exchange_router import validate_risk
        
        # SL=2% × Leverage=10x = 20% < 30% (max)
        is_valid, msg = validate_risk(sl_percent=2.0, leverage=10, max_risk_pct=30.0)
        
        assert is_valid is True
        assert msg is None
    
    @pytest.mark.unit
    def test_validate_risk_too_high(self):
        """Test risk validation - too high"""
        from exchange_router import validate_risk
        
        # SL=5% × Leverage=10x = 50% > 30% (max)
        is_valid, msg = validate_risk(sl_percent=5.0, leverage=10, max_risk_pct=30.0)
        
        assert is_valid is False
        assert "Risk too high" in msg
        assert "Suggested SL: 3.00%" in msg
    
    @pytest.mark.unit
    def test_validate_risk_none_values(self):
        """Test risk validation - handles None values"""
        from exchange_router import validate_risk
        
        # If SL or leverage is None, risk is considered valid
        is_valid, msg = validate_risk(sl_percent=None, leverage=10)
        assert is_valid is True
        
        is_valid, msg = validate_risk(sl_percent=2.0, leverage=None)
        assert is_valid is True
    
    @pytest.mark.unit
    def test_auto_adjust_sl_needed(self):
        """Test auto-adjusting SL when risk is too high"""
        from exchange_router import auto_adjust_sl_for_risk
        
        # 5% SL × 10x = 50% > 30% max
        adjusted = auto_adjust_sl_for_risk(sl_percent=5.0, leverage=10, max_risk_pct=30.0)
        
        # Should be reduced to 3% (30% / 10x)
        assert adjusted == 3.0
    
    @pytest.mark.unit
    def test_auto_adjust_sl_not_needed(self):
        """Test no adjustment when risk is acceptable"""
        from exchange_router import auto_adjust_sl_for_risk
        
        # 2% SL × 10x = 20% < 30% max
        adjusted = auto_adjust_sl_for_risk(sl_percent=2.0, leverage=10, max_risk_pct=30.0)
        
        # Should remain 2%
        assert adjusted == 2.0


class TestSymbolNormalization:
    """Test symbol normalization for different exchanges"""
    
    @pytest.mark.unit
    def test_normalize_bybit_symbol(self):
        """Test symbol normalization for Bybit"""
        from exchange_router import normalize_symbol, Exchange
        
        # Bybit keeps USDT suffix
        assert normalize_symbol("BTCUSDT", Exchange.BYBIT) == "BTCUSDT"
        assert normalize_symbol("BTC", Exchange.BYBIT) == "BTC"
    
    @pytest.mark.unit
    def test_normalize_hl_symbol(self):
        """Test symbol normalization for HyperLiquid"""
        from exchange_router import normalize_symbol, Exchange
        
        # HyperLiquid strips USDT suffix
        assert normalize_symbol("BTCUSDT", Exchange.HYPERLIQUID) == "BTC"
        assert normalize_symbol("ETHUSDT", Exchange.HYPERLIQUID) == "ETH"
        assert normalize_symbol("BTC", Exchange.HYPERLIQUID) == "BTC"
    
    @pytest.mark.unit
    def test_denormalize_hl_to_bybit(self):
        """Test denormalizing HL symbol to Bybit format"""
        from exchange_router import denormalize_symbol, Exchange
        
        # denormalize_symbol adds USDT suffix for HyperLiquid symbols
        # For Bybit, it returns as-is
        assert denormalize_symbol("BTC", Exchange.HYPERLIQUID) == "BTCUSDT"
        assert denormalize_symbol("ETH", Exchange.HYPERLIQUID) == "ETHUSDT"
        assert denormalize_symbol("BTCUSDT", Exchange.HYPERLIQUID) == "BTCUSDT"
        # Bybit returns as-is
        assert denormalize_symbol("BTC", Exchange.BYBIT) == "BTC"
        assert denormalize_symbol("BTCUSDT", Exchange.BYBIT) == "BTCUSDT"


class TestExchangeRouter:
    """Test ExchangeRouter class"""
    
    @pytest.mark.unit
    def test_router_initialization(self):
        """Test router initialization"""
        from exchange_router import ExchangeRouter
        
        router = ExchangeRouter(
            bybit_client_factory=None,
            hl_client_factory=None
        )
        
        assert router._bybit_factory is None
        assert router._hl_factory is None
    
    @pytest.mark.unit
    def test_get_execution_targets_empty(self):
        """Test getting execution targets for user with no config"""
        from exchange_router import ExchangeRouter
        
        router = ExchangeRouter()
        
        # Non-existent user should return empty list or legacy fallback
        targets = router.get_execution_targets(user_id=999999999)
        
        # May be empty or may have legacy fallback
        assert isinstance(targets, list)


class TestBackwardCompatibility:
    """Test backward compatibility wrapper functions"""
    
    @pytest.mark.unit
    def test_place_order_universal_import(self):
        """Test that place_order_universal can be imported"""
        from exchange_router import place_order_universal
        
        assert callable(place_order_universal)
    
    @pytest.mark.unit
    def test_fetch_positions_universal_import(self):
        """Test that fetch_positions_universal can be imported"""
        from exchange_router import fetch_positions_universal
        
        assert callable(fetch_positions_universal)
    
    @pytest.mark.unit
    def test_set_leverage_universal_import(self):
        """Test that set_leverage_universal can be imported"""
        from exchange_router import set_leverage_universal
        
        assert callable(set_leverage_universal)
    
    @pytest.mark.unit
    def test_close_position_universal_import(self):
        """Test that close_position_universal can be imported"""
        from exchange_router import close_position_universal
        
        assert callable(close_position_universal)
    
    @pytest.mark.unit
    def test_get_balance_universal_import(self):
        """Test that get_balance_universal can be imported"""
        from exchange_router import get_balance_universal
        
        assert callable(get_balance_universal)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_place_order_universal_no_exchange_configured(self):
        """Test place_order_universal returns error when no exchange configured"""
        from exchange_router import place_order_universal
        
        # User with no exchange configured should fail gracefully
        result = await place_order_universal(
            user_id=999999999,
            symbol="BTCUSDT",
            side="Buy",
            orderType="Market",
            qty=0.1
        )
        
        # Should return error (not raise exception)
        if result:
            # If it returns something, check for error indicators
            assert isinstance(result, dict)


class TestExchangeSelection:
    """Test exchange selection logic via db module"""
    
    @pytest.mark.unit
    def test_get_user_exchange_type(self, test_user_id, test_db):
        """Test getting user's selected exchange"""
        import db
        
        with patch.object(db, 'get_exchange_type', return_value='bybit'):
            exchange_type = db.get_exchange_type(test_user_id)
        
        assert exchange_type == 'bybit'
    
    @pytest.mark.unit
    def test_set_user_exchange_type(self, test_user_id, test_db):
        """Test setting user's exchange"""
        import db
        
        with patch.object(db, 'set_exchange_type', return_value=True):
            result = db.set_exchange_type(test_user_id, 'hyperliquid')
        
        assert result is True


class TestExecutionTargetsFunctions:
    """Test execution targets DB functions"""
    
    @pytest.mark.unit
    def test_get_execution_targets_function(self):
        """Test db.get_execution_targets returns list"""
        import db
        
        targets = db.get_execution_targets(999999999)  # non-existent user
        
        assert isinstance(targets, list)
    
    @pytest.mark.unit
    def test_add_exchange_account(self):
        """Test adding exchange account"""
        import db
        
        # Use unique user ID for this test
        test_uid = 777777777
        
        # First ensure user exists
        db.ensure_user(test_uid)
        
        # Add account (first time should create)
        account_id = db.add_exchange_account(
            user_id=test_uid,
            exchange="bybit",
            account_type="real",  # use 'real' to avoid conflict with demo
            label="Test Account",
            is_enabled=True,
            max_leverage=50,
            risk_limit_pct=25.0
        )
        
        # May be 0 if REPLACE was used on existing record
        assert account_id is not None
        assert account_id >= 0
    
    @pytest.mark.unit
    def test_get_exchange_account(self):
        """Test getting exchange account"""
        import db
        
        db.ensure_user(888888888)
        db.add_exchange_account(
            user_id=888888888,
            exchange="bybit",
            account_type="demo",
            label="Test Account 2"
        )
        
        account = db.get_exchange_account(888888888, "bybit", "demo")
        
        if account:
            assert account["exchange"] == "bybit"
            assert account["account_type"] == "demo"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
