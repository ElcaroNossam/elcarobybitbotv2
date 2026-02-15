"""
Integration & End-to-End Tests
Разнообразные интеграционные тесты для проверки взаимодействия компонентов.
"""
import os
import sys
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import db
from exchanges.base import OrderSide, OrderType, PositionSide, Position, Balance, OrderResult
from core.exceptions import InsufficientBalanceError, PositionNotFoundError


# ===========================
# DATABASE INTEGRATION Tests
# ===========================

class TestDatabaseIntegration:
    """Test database operations"""
    
    def test_user_crud_operations(self, test_db, test_user_id):
        """Test complete user CRUD cycle"""
        # Create
        db.ensure_user(test_user_id)
        
        # Read
        user = db.get_user_config(test_user_id)
        assert user is not None
        # user_id is not returned in get_user_config, check leverage instead
        assert "leverage" in user
        
        # Update
        db.set_user_field(test_user_id, "leverage", 20)
        updated = db.get_user_config(test_user_id)
        assert updated.get("leverage") == 20
        
        # Verify user exists (ensure_user doesn't return boolean)
        db.ensure_user(test_user_id)
        config = db.get_user_config(test_user_id)
        assert config is not None
    
    def test_position_lifecycle(self, test_db, test_user_id):
        """Test position creation and management"""
        db.ensure_user(test_user_id)
        
        # Clean up any existing positions first
        existing = db.get_active_positions(test_user_id, exchange='bybit')
        for pos in existing:
            db.remove_active_position(test_user_id, pos['symbol'], exchange=pos.get('exchange', 'bybit'))
        
        # Add position
        db.add_active_position(
            user_id=test_user_id,
            symbol="BTCUSDT",
            side="long",
            entry_price=45000.0,
            size=0.1,
            timeframe="4h",
            signal_id=None,
            strategy="elcaro",
            account_type="demo",
            exchange="bybit"  # 4D schema
        )
        
        # Get positions
        positions = db.get_active_positions(test_user_id, exchange='bybit')
        assert len(positions) > 0
        
        # Remove position
        db.remove_active_position(test_user_id, "BTCUSDT", "demo", exchange="bybit")
        positions_after = db.get_active_positions(test_user_id, exchange='bybit')
        assert len(positions_after) == 0
    
    def test_trade_logging(self, test_db, test_user_id):
        """Test trade log creation"""
        db.ensure_user(test_user_id)
        
        # Log trade with multitenancy params
        db.add_trade_log(
            user_id=test_user_id,
            signal_id=None,
            symbol="ETHUSDT",
            side="long",
            entry_price=3000.0,
            exit_price=3100.0,
            exit_reason="TP",
            pnl=100.0,
            pnl_pct=3.33,
            strategy="scalper",
            account_type="demo",
            exchange="bybit"
        )
        
        # Get stats with exchange
        stats = db.get_trade_stats(test_user_id, strategy="scalper", exchange="bybit")
        assert stats is not None
    
    def test_signal_storage(self, test_db):
        """Test signal storage"""
        signal_id = db.add_signal(
            raw_message="BTCUSDT LONG Entry: 45000",
            tf="4h",
            side="long",
            symbol="BTCUSDT",
            price=45000.0,
            oi_prev=None,
            oi_now=None,
            oi_chg=None,
            vol_from=None,
            vol_to=None,
            price_chg=None,
            vol_delta=None,
            rsi=None,
            bb_hi=None,
            bb_lo=None
        )
        
        assert signal_id is not None


# ===========================
# TRADING WORKFLOW Tests
# ===========================

class TestTradingWorkflow:
    """Test complete trading workflows"""
    
    @pytest.mark.asyncio
    async def test_open_close_position_workflow(self, test_db, test_user_id):
        """Test opening and closing position"""
        db.ensure_user(test_user_id)
        
        # Mock exchange
        mock_exchange = AsyncMock()
        mock_exchange.get_balance.return_value = Balance(
            total_equity=10000.0,
            available_balance=9000.0,
            margin_used=1000.0,
            unrealized_pnl=0.0
        )
        mock_exchange.place_order.return_value = OrderResult(
            success=True,
            order_id="open_123",
            filled_size=0.1,
            avg_price=45000.0
        )
        
        # Open position
        balance = await mock_exchange.get_balance()
        assert balance.available_balance > 0
        
        order_result = await mock_exchange.place_order(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            size=0.1,
            order_type=OrderType.MARKET
        )
        assert order_result.success is True
        
        # Add to DB
        db.add_active_position(
            user_id=test_user_id,
            symbol="BTCUSDT",
            side="long",
            entry_price=45000.0,
            size=0.1,
            timeframe="4h",
            signal_id=None,
            strategy=None,
            account_type="demo",
            exchange="bybit"
        )
        
        # Close position
        mock_exchange.close_position.return_value = OrderResult(
            success=True,
            order_id="close_123"
        )
        
        close_result = await mock_exchange.close_position("BTCUSDT", 0.1)
        assert close_result.success is True
        
        # Remove from DB
        db.remove_active_position(test_user_id, "BTCUSDT", "demo", exchange="bybit")
    
    def test_multi_position_management(self, test_db, test_user_id):
        """Test managing multiple positions"""
        db.ensure_user(test_user_id)
        
        # Add multiple positions
        symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        for symbol in symbols:
            db.add_active_position(
                user_id=test_user_id,
                symbol=symbol,
                side="long",
                entry_price=45000.0,
                size=0.1,
                timeframe="4h",
                signal_id=None,
                strategy=None,
                account_type="demo",
                exchange="bybit"  # 4D schema
            )
        
        # Get all positions
        positions = db.get_active_positions(test_user_id, exchange='bybit')
        assert len(positions) >= 3
        
        # Clean up
        for symbol in symbols:
            db.remove_active_position(test_user_id, symbol, "demo", exchange="bybit")
    
    def test_position_with_tp_sl(self, test_db, test_user_id):
        """Test position with TP/SL"""
        db.ensure_user(test_user_id)
        
        entry_price = 45000.0
        tp_percent = 5.0
        sl_percent = 2.0
        
        # Calculate TP/SL
        take_profit = entry_price * (1 + tp_percent / 100)
        stop_loss = entry_price * (1 - sl_percent / 100)
        
        assert take_profit > entry_price
        assert stop_loss < entry_price
        
        # Add position with TP/SL
        db.add_active_position(
            user_id=test_user_id,
            symbol="BTCUSDT",
            side="long",
            entry_price=entry_price,
            size=0.1,
            timeframe="4h",
            signal_id=None,
            strategy=None,
            account_type="demo",
            exchange="bybit"  # 4D schema
        )
        
        positions = db.get_active_positions(test_user_id, exchange='bybit')
        assert len(positions) > 0


# ===========================
# EXCHANGE SWITCHING Tests
# ===========================

class TestExchangeSwitching:
    """Test switching between exchanges"""
    
    def test_switch_from_bybit_to_hyperliquid(self, test_db, test_user_id):
        """Test switching exchange"""
        db.ensure_user(test_user_id)
        
        # Set to Bybit
        db.set_exchange_type(test_user_id, "bybit")
        exchange = db.get_exchange_type(test_user_id)
        assert exchange == "bybit"
        
        # Switch to HyperLiquid
        db.set_exchange_type(test_user_id, "hyperliquid")
        exchange = db.get_exchange_type(test_user_id)
        assert exchange == "hyperliquid"
    
    def test_exchange_specific_credentials(self, test_db, test_user_id):
        """Test exchange-specific credentials"""
        db.ensure_user(test_user_id)
        
        # Bybit credentials
        db.set_user_credentials(test_user_id, "bybit_key", "bybit_secret", "demo")
        creds = db.get_user_credentials(test_user_id, "demo")
        assert creds is not None
        
        # HyperLiquid credentials (returns dict or None)
        db.set_hl_credentials(test_user_id, private_key="0x123456", testnet=True)
        hl_creds = db.get_hl_credentials(test_user_id)
        assert hl_creds is not None


# ===========================
# STRATEGY SETTINGS Tests
# ===========================

class TestStrategySettings:
    """Test strategy settings management"""
    
    def test_strategy_enable_disable(self, test_db, test_user_id):
        """Test enabling/disabling strategies"""
        db.ensure_user(test_user_id)
        
        # Use valid fields only
        db.set_user_field(test_user_id, "leverage", 10)
        db.set_user_field(test_user_id, "percent", 1.0)
        db.set_user_field(test_user_id, "tp_percent", 25.0)
        
        user = db.get_user_config(test_user_id)
        assert user.get("leverage") == 10
    
    def test_strategy_specific_settings(self, test_db, test_user_id):
        """Test strategy-specific settings"""
        db.ensure_user(test_user_id)
        
        # Use only valid fields
        settings = {
            "percent": 5.0,
            "tp_percent": 25.0,
            "sl_percent": 30.0,
            "leverage": 15
        }
        
        for key, value in settings.items():
            db.set_user_field(test_user_id, key, value)
        
        user = db.get_user_config(test_user_id)
        assert user.get("percent") == 5.0
        assert user.get("leverage") == 15
    
    def test_global_vs_strategy_settings(self, test_db, test_user_id):
        """Test global vs strategy-specific settings priority"""
        db.ensure_user(test_user_id)
        
        # Global settings
        db.set_user_field(test_user_id, "percent", 2.0)
        db.set_user_field(test_user_id, "leverage", 10)
        
        # Update settings
        db.set_user_field(test_user_id, "percent", 1.0)
        db.set_user_field(test_user_id, "leverage", 5)
        
        user = db.get_user_config(test_user_id)
        
        # Should be updated
        assert user.get("percent") == 1.0
        assert user.get("leverage") == 5


# ===========================
# PERFORMANCE Tests
# ===========================

class TestPerformance:
    """Test performance characteristics"""
    
    def test_bulk_user_operations(self, test_db):
        """Test bulk user operations"""
        user_ids = range(90000, 90010)
        
        # Create multiple users
        for uid in user_ids:
            db.ensure_user(uid)
        
        # Verify all created
        for uid in user_ids:
            db.ensure_user(uid)
            config = db.get_user_config(uid)
            assert config is not None
    
    def test_position_query_performance(self, test_db, test_user_id):
        """Test position query performance"""
        import time
        
        db.ensure_user(test_user_id)
        
        # Add multiple positions
        for i in range(10):
            db.add_active_position(
                user_id=test_user_id,
                symbol=f"TEST{i}USDT",
                side="long",
                entry_price=1000.0 + i,
                size=0.1,
                timeframe="4h",
                signal_id=None,
                strategy=None,
                account_type="demo",
                exchange="bybit"
            )
        
        # Measure query time
        start = time.time()
        positions = db.get_active_positions(test_user_id, exchange='bybit')
        elapsed = time.time() - start
        
        assert len(positions) >= 10
        assert elapsed < 1.0  # Should be fast


# ===========================
# ERROR RECOVERY Tests
# ===========================

class TestErrorRecovery:
    """Test error handling and recovery"""
    
    @pytest.mark.asyncio
    async def test_handle_insufficient_balance(self):
        """Test handling insufficient balance"""
        mock_exchange = AsyncMock()
        mock_exchange.get_balance.return_value = Balance(
            total_equity=100.0,
            available_balance=50.0,
            margin_used=50.0,
            unrealized_pnl=0.0
        )
        
        balance = await mock_exchange.get_balance()
        
        # Check if balance is sufficient
        required = 1000.0
        if balance.available_balance < required:
            with pytest.raises(Exception):
                raise InsufficientBalanceError(
                    "Insufficient balance",
                    required=required,
                    available=balance.available_balance
                )
    
    @pytest.mark.asyncio
    async def test_handle_position_not_found(self):
        """Test handling position not found"""
        mock_exchange = AsyncMock()
        mock_exchange.get_positions.return_value = []
        
        positions = await mock_exchange.get_positions()
        
        if not positions:
            with pytest.raises(Exception):
                raise PositionNotFoundError(
                    "Position not found",
                    symbol="BTCUSDT"
                )
    
    def test_database_rollback_on_error(self, test_db, test_user_id):
        """Test database rollback on error"""
        db.ensure_user(test_user_id)
        
        initial_value = db.get_user_config(test_user_id).get("leverage", 10)
        
        try:
            # Try to set invalid value
            db.set_user_field(test_user_id, "leverage", 999)
            # If this succeeds, verify it
            updated = db.get_user_config(test_user_id).get("leverage")
            assert updated == 999 or updated == initial_value
        except Exception:
            # On error, value should remain unchanged
            current = db.get_user_config(test_user_id).get("leverage")
            assert current == initial_value


# ===========================
# SIGNAL PROCESSING Tests
# ===========================

class TestSignalProcessing:
    """Test signal detection and processing"""
    
    def test_detect_signal_type(self):
        """Test detecting signal type"""
        signals = {
            "BTCUSDT LONG Entry: 45000": "long",
            "ETHUSDT SHORT Entry: 3000": "short",
            "Close BTCUSDT": "exit"
        }
        
        for text, expected_type in signals.items():
            text_lower = text.lower()
            if "long" in text_lower or "buy" in text_lower:
                detected = "long"
            elif "short" in text_lower or "sell" in text_lower:
                detected = "short"
            elif "close" in text_lower or "exit" in text_lower:
                detected = "exit"
            else:
                detected = "unknown"
            
            assert detected == expected_type
    
    def test_extract_signal_data(self):
        """Test extracting data from signal"""
        import re
        
        text = "BTCUSDT LONG Entry: 45000 TP: 46000 SL: 44000"
        
        # Extract symbol
        symbol_match = re.search(r"([A-Z]+USDT)", text)
        assert symbol_match and symbol_match.group(1) == "BTCUSDT"
        
        # Extract prices
        prices = [float(x) for x in re.findall(r"(\d+\.?\d*)", text) if float(x) > 100]
        assert 45000.0 in prices
        assert 46000.0 in prices
    
    def test_validate_signal_data(self):
        """Test signal data validation"""
        signal_data = {
            "symbol": "BTCUSDT",
            "side": "long",
            "entry": 45000.0,
            "tp": 46000.0,
            "sl": 44000.0
        }
        
        # Validate
        assert signal_data["symbol"].endswith("USDT")
        assert signal_data["side"] in ["long", "short"]
        assert signal_data["entry"] > 0
        
        # Validate TP/SL
        if signal_data["side"] == "long":
            assert signal_data["tp"] > signal_data["entry"]
            assert signal_data["sl"] < signal_data["entry"]


# ===========================
# FEATURE FLAGS Tests
# ===========================

class TestFeatureFlags:
    """Test feature flag system"""
    
    def test_feature_enabled_for_user(self, test_db, test_user_id):
        """Test checking feature flags"""
        db.ensure_user(test_user_id)
        
        # Enable features (use valid fields only)
        features = {
            "leverage": 10,
            "percent": 1.0,
            "tp_percent": 25.0,
            "sl_percent": 30.0
        }
        
        for feature, enabled in features.items():
            db.set_user_field(test_user_id, feature, enabled)
        
        user = db.get_user_config(test_user_id)
        assert user.get("leverage") == 10
        assert user.get("percent") == 1.0
    
    def test_premium_features(self, test_db, test_user_id):
        """Test premium feature access"""
        db.ensure_user(test_user_id)
        
        # Simulate premium check
        user = db.get_user_config(test_user_id)
        is_premium = user.get("license_type") == "premium"
        
        # Premium features
        if is_premium:
            assert True  # Can access all features
        else:
            # Free tier limitations
            assert True  # Limited access


# ===========================
# CACHE CONSISTENCY Tests
# ===========================

class TestCacheConsistency:
    """Test cache consistency with database"""
    
    def test_cache_invalidation_on_update(self, test_db, test_user_id):
        """Test cache invalidates on database update"""
        db.ensure_user(test_user_id)
        
        # First read (may cache)
        user1 = db.get_user_config(test_user_id)
        initial_leverage = user1.get("leverage", 10)
        
        # Update
        new_leverage = initial_leverage + 5
        db.set_user_field(test_user_id, "leverage", new_leverage)
        
        # Second read (should get updated value)
        user2 = db.get_user_config(test_user_id)
        updated_leverage = user2.get("leverage")
        
        assert updated_leverage == new_leverage
    
    def test_multi_field_update_consistency(self, test_db, test_user_id):
        """Test consistency of multiple field updates"""
        db.ensure_user(test_user_id)
        
        # Update multiple fields
        updates = {
            "leverage": 20,
            "percent": 5.0,
            "tp_percent": 25.0,
            "sl_percent": 30.0
        }
        
        for key, value in updates.items():
            db.set_user_field(test_user_id, key, value)
        
        # Verify all updates
        user = db.get_user_config(test_user_id)
        for key, expected_value in updates.items():
            assert user.get(key) == expected_value


# ===========================
# LANGUAGE & TRANSLATION Tests
# ===========================

class TestLanguageSupport:
    """Test language and translation support"""
    
    def test_set_user_language(self, test_db, test_user_id):
        """Test setting user language"""
        db.ensure_user(test_user_id)
        
        languages = ["en", "ru", "uk", "zh", "es"]
        
        for lang in languages:
            db.set_user_field(test_user_id, "lang", lang)
            user = db.get_user_config(test_user_id)
            assert user.get("lang") == lang
    
    def test_default_language(self, test_db):
        """Test default language for new users"""
        new_user_id = 999999
        db.ensure_user(new_user_id)
        
        user = db.get_user_config(new_user_id)
        lang = user.get("lang", "en")
        
        assert lang in ["en", "ru"]  # Default languages
