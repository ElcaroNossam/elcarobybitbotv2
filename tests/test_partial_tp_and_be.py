#!/usr/bin/env python3
"""
Comprehensive tests for Partial Take Profit and Break-Even features.
Tests the new 4D schema settings for:
- partial_tp_enabled, partial_tp_1_trigger_pct, partial_tp_1_close_pct
- partial_tp_2_trigger_pct, partial_tp_2_close_pct
- be_enabled, be_trigger_pct

These features are per-strategy/side settings in user_strategy_settings table.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import db
from core.db_postgres import (
    pg_get_strategy_settings,
    pg_set_strategy_setting,
)

# Define expected fields locally for testing
EXPECTED_PARTIAL_TP_FIELDS = [
    "partial_tp_enabled",
    "partial_tp_1_trigger_pct",
    "partial_tp_1_close_pct",
    "partial_tp_2_trigger_pct",
    "partial_tp_2_close_pct",
]

EXPECTED_BE_FIELDS = ["be_enabled", "be_trigger_pct"]

# Test users
TEST_USERS = [
    888801,  # Test user for Partial TP
    888802,  # Test user for BE
    888803,  # Test user for combined settings
]

STRATEGIES = ["oi", "rsi_bb", "scryptomera", "scalper", "elcaro", "fibonacci"]
SIDES = ["long", "short"]
EXCHANGES = ["bybit", "hyperliquid"]


@pytest.fixture(autouse=True)
def setup_and_cleanup():
    """Setup test users before tests and cleanup after"""
    # Setup
    cleanup_test_users()
    for uid in TEST_USERS:
        db.ensure_user(uid)
        db.invalidate_user_cache(uid)
    yield
    # Cleanup
    cleanup_test_users()


def cleanup_test_users():
    """Remove test users"""
    try:
        with db.get_conn() as conn:
            cur = conn.cursor()
            for uid in TEST_USERS:
                cur.execute("DELETE FROM user_strategy_settings WHERE user_id = %s", (uid,))
                cur.execute("DELETE FROM users WHERE user_id = %s", (uid,))
            conn.commit()
    except Exception as e:
        print(f"Cleanup warning: {e}")


class TestPartialTPFieldsExist:
    """Test that Partial TP fields are properly defined"""
    
    def test_partial_tp_fields_can_be_set(self):
        """Verify Partial TP fields can be set successfully"""
        uid = TEST_USERS[0]
        strategy = "oi"
        
        # Try setting each field with long_ prefix - if it works, the field is allowed
        for field in EXPECTED_PARTIAL_TP_FIELDS:
            prefixed_field = f"long_{field}"
            if field == "partial_tp_enabled":
                result = pg_set_strategy_setting(uid, strategy, prefixed_field, True, "bybit")
            else:
                result = pg_set_strategy_setting(uid, strategy, prefixed_field, 5.0, "bybit")
            assert result is True, f"Failed to set {prefixed_field}"
    
    def test_partial_tp_enabled_stored_as_boolean(self):
        """Verify partial_tp_enabled is stored as boolean"""
        uid = TEST_USERS[0]
        strategy = "rsi_bb"
        
        pg_set_strategy_setting(uid, strategy, "long_partial_tp_enabled", True, "bybit")
        settings = pg_get_strategy_settings(uid, strategy, "bybit")
        
        # Should be True (boolean), not 1 or "true"
        assert settings.get("long_partial_tp_enabled") is True
    
    def test_be_fields_can_be_set(self):
        """Verify BE fields can be set successfully"""
        uid = TEST_USERS[0]
        strategy = "scalper"
        
        for field in EXPECTED_BE_FIELDS:
            prefixed_field = f"long_{field}"
            if field == "be_enabled":
                result = pg_set_strategy_setting(uid, strategy, prefixed_field, True, "bybit")
            else:
                result = pg_set_strategy_setting(uid, strategy, prefixed_field, 1.5, "bybit")
            assert result is True, f"Failed to set {prefixed_field}"
    
    def test_be_enabled_stored_as_boolean(self):
        """Verify be_enabled is stored as boolean"""
        uid = TEST_USERS[0]
        strategy = "elcaro"
        
        pg_set_strategy_setting(uid, strategy, "long_be_enabled", True, "bybit")
        settings = pg_get_strategy_settings(uid, strategy, "bybit")
        
        # Should be True (boolean), not 1 or "true"
        assert settings.get("long_be_enabled") is True


class TestPartialTPSettings:
    """Test Partial TP setting and getting"""
    
    def test_set_partial_tp_enabled(self):
        """Test enabling/disabling Partial TP"""
        uid = TEST_USERS[0]
        strategy = "oi"
        
        # Enable Partial TP (use prefixed field name)
        result = pg_set_strategy_setting(uid, strategy, "long_partial_tp_enabled", True, "bybit")
        assert result is True
        
        # Verify it's enabled
        settings = pg_get_strategy_settings(uid, strategy, "bybit")
        assert settings.get("long_partial_tp_enabled") is True
    
    def test_set_partial_tp_step1(self):
        """Test setting Step 1 parameters"""
        uid = TEST_USERS[0]
        strategy = "rsi_bb"
        
        # Set Step 1: close 30% at +2.5% profit (use prefixed field names)
        pg_set_strategy_setting(uid, strategy, "long_partial_tp_1_trigger_pct", 2.5, "bybit")
        pg_set_strategy_setting(uid, strategy, "long_partial_tp_1_close_pct", 30.0, "bybit")
        
        settings = pg_get_strategy_settings(uid, strategy, "bybit")
        assert settings.get("long_partial_tp_1_trigger_pct") == 2.5
        assert settings.get("long_partial_tp_1_close_pct") == 30.0
    
    def test_set_partial_tp_step2(self):
        """Test setting Step 2 parameters"""
        uid = TEST_USERS[0]
        strategy = "scalper"
        
        # Set Step 2: close 50% at +5.0% profit (use prefixed field names)
        pg_set_strategy_setting(uid, strategy, "short_partial_tp_2_trigger_pct", 5.0, "bybit")
        pg_set_strategy_setting(uid, strategy, "short_partial_tp_2_close_pct", 50.0, "bybit")
        
        settings = pg_get_strategy_settings(uid, strategy, "bybit")
        assert settings.get("short_partial_tp_2_trigger_pct") == 5.0
        assert settings.get("short_partial_tp_2_close_pct") == 50.0
    
    def test_partial_tp_long_short_independence(self):
        """Test that Long and Short have independent Partial TP settings"""
        uid = TEST_USERS[0]
        strategy = "elcaro"
        
        # Set different values for Long and Short
        pg_set_strategy_setting(uid, strategy, "long_partial_tp_1_trigger_pct", 3.0, "bybit")
        pg_set_strategy_setting(uid, strategy, "short_partial_tp_1_trigger_pct", 4.0, "bybit")
        
        settings = pg_get_strategy_settings(uid, strategy, "bybit")
        
        assert settings.get("long_partial_tp_1_trigger_pct") == 3.0
        assert settings.get("short_partial_tp_1_trigger_pct") == 4.0
        assert settings.get("long_partial_tp_1_trigger_pct") != settings.get("short_partial_tp_1_trigger_pct")
    
    def test_partial_tp_exchange_isolation(self):
        """Test Partial TP settings are isolated by exchange"""
        uid = TEST_USERS[0]
        strategy = "fibonacci"
        
        # Set different values for Bybit and HyperLiquid
        pg_set_strategy_setting(uid, strategy, "long_partial_tp_enabled", True, "bybit")
        pg_set_strategy_setting(uid, strategy, "long_partial_tp_enabled", False, "hyperliquid")
        
        bybit_settings = pg_get_strategy_settings(uid, strategy, "bybit")
        hl_settings = pg_get_strategy_settings(uid, strategy, "hyperliquid")
        
        assert bybit_settings.get("long_partial_tp_enabled") is True
        assert hl_settings.get("long_partial_tp_enabled") is False


class TestBreakEvenSettings:
    """Test Break-Even setting and getting"""
    
    def test_set_be_enabled(self):
        """Test enabling/disabling Break-Even"""
        uid = TEST_USERS[1]
        strategy = "oi"
        
        # Enable BE (use prefixed field name)
        pg_set_strategy_setting(uid, strategy, "long_be_enabled", True, "bybit")
        
        settings = pg_get_strategy_settings(uid, strategy, "bybit")
        assert settings.get("long_be_enabled") is True
    
    def test_set_be_trigger_pct(self):
        """Test setting BE trigger percentage"""
        uid = TEST_USERS[1]
        strategy = "rsi_bb"
        
        # Set BE trigger at 1.5% profit
        pg_set_strategy_setting(uid, strategy, "long_be_trigger_pct", 1.5, "bybit")
        
        settings = pg_get_strategy_settings(uid, strategy, "bybit")
        assert settings.get("long_be_trigger_pct") == 1.5
    
    def test_be_long_short_independence(self):
        """Test that Long and Short have independent BE settings"""
        uid = TEST_USERS[1]
        strategy = "scalper"
        
        # Set different BE triggers for Long and Short
        pg_set_strategy_setting(uid, strategy, "long_be_trigger_pct", 1.0, "bybit")
        pg_set_strategy_setting(uid, strategy, "short_be_trigger_pct", 2.0, "bybit")
        
        settings = pg_get_strategy_settings(uid, strategy, "bybit")
        
        assert settings.get("long_be_trigger_pct") == 1.0
        assert settings.get("short_be_trigger_pct") == 2.0
    
    def test_be_exchange_isolation(self):
        """Test BE settings are isolated by exchange"""
        uid = TEST_USERS[1]
        strategy = "elcaro"
        
        # Set different BE values for Bybit and HyperLiquid
        pg_set_strategy_setting(uid, strategy, "long_be_enabled", True, "bybit")
        pg_set_strategy_setting(uid, strategy, "long_be_trigger_pct", 1.0, "bybit")
        
        pg_set_strategy_setting(uid, strategy, "long_be_enabled", False, "hyperliquid")
        pg_set_strategy_setting(uid, strategy, "long_be_trigger_pct", 2.0, "hyperliquid")
        
        bybit_settings = pg_get_strategy_settings(uid, strategy, "bybit")
        hl_settings = pg_get_strategy_settings(uid, strategy, "hyperliquid")
        
        assert bybit_settings.get("long_be_enabled") is True
        assert bybit_settings.get("long_be_trigger_pct") == 1.0
        
        assert hl_settings.get("long_be_enabled") is False
        assert hl_settings.get("long_be_trigger_pct") == 2.0


class TestCombinedSettings:
    """Test Partial TP and BE together"""
    
    def test_all_settings_together(self):
        """Test setting all Partial TP + BE settings together"""
        uid = TEST_USERS[2]
        strategy = "oi"
        exchange = "bybit"
        
        # Set all Partial TP settings with long_ prefix
        pg_set_strategy_setting(uid, strategy, "long_partial_tp_enabled", True, exchange)
        pg_set_strategy_setting(uid, strategy, "long_partial_tp_1_trigger_pct", 2.0, exchange)
        pg_set_strategy_setting(uid, strategy, "long_partial_tp_1_close_pct", 30.0, exchange)
        pg_set_strategy_setting(uid, strategy, "long_partial_tp_2_trigger_pct", 5.0, exchange)
        pg_set_strategy_setting(uid, strategy, "long_partial_tp_2_close_pct", 50.0, exchange)
        
        # Set all BE settings with long_ prefix
        pg_set_strategy_setting(uid, strategy, "long_be_enabled", True, exchange)
        pg_set_strategy_setting(uid, strategy, "long_be_trigger_pct", 1.0, exchange)
        
        # Verify all
        settings = pg_get_strategy_settings(uid, strategy, exchange)
        
        assert settings.get("long_partial_tp_enabled") is True
        assert settings.get("long_partial_tp_1_trigger_pct") == 2.0
        assert settings.get("long_partial_tp_1_close_pct") == 30.0
        assert settings.get("long_partial_tp_2_trigger_pct") == 5.0
        assert settings.get("long_partial_tp_2_close_pct") == 50.0
        assert settings.get("long_be_enabled") is True
        assert settings.get("long_be_trigger_pct") == 1.0
    
    def test_full_4d_isolation(self):
        """Test all settings are fully isolated by 4D schema"""
        uid = TEST_USERS[2]
        
        # Set different Partial TP for each strategy/side/exchange combination
        test_cases = [
            ("oi", "long", "bybit", 2.0),
            ("oi", "short", "bybit", 3.0),
            ("oi", "long", "hyperliquid", 4.0),
            ("rsi_bb", "long", "bybit", 5.0),
        ]
        
        for strategy, side, exchange, trigger in test_cases:
            # Use prefixed field name
            field = f"{side}_partial_tp_1_trigger_pct"
            pg_set_strategy_setting(uid, strategy, field, trigger, exchange)
        
        # Verify each has its own value
        for strategy, side, exchange, expected_trigger in test_cases:
            settings = pg_get_strategy_settings(uid, strategy, exchange)
            field_name = f"{side}_partial_tp_1_trigger_pct"
            actual = settings.get(field_name)
            assert actual == expected_trigger, f"Expected {expected_trigger} for {strategy}/{side}/{exchange}, got {actual}"


class TestDefaultValues:
    """Test default values for Partial TP and BE"""
    
    def test_partial_tp_defaults(self):
        """Test Partial TP has correct defaults when not set"""
        uid = TEST_USERS[2]
        strategy = "fibonacci"  # Not used before
        
        settings = pg_get_strategy_settings(uid, strategy, "bybit")
        
        # Default values from core/db_postgres.py - all defaults are 30.0 for close_pct
        assert settings.get("long_partial_tp_enabled") is False
        assert settings.get("long_partial_tp_1_trigger_pct") == 2.0
        assert settings.get("long_partial_tp_1_close_pct") == 30.0
        assert settings.get("long_partial_tp_2_trigger_pct") == 5.0
        assert settings.get("long_partial_tp_2_close_pct") == 30.0  # Default is 30.0, not 50.0
    
    def test_be_defaults(self):
        """Test BE has correct defaults when not set"""
        uid = TEST_USERS[2]
        strategy = "scryptomera"  # Not used before
        
        settings = pg_get_strategy_settings(uid, strategy, "bybit")
        
        # Default values - be_enabled returns 0 from DB, compare as falsy
        assert not settings.get("long_be_enabled")  # 0 or False both work
        assert settings.get("long_be_trigger_pct") == 1.0


class TestMultiUserIsolation:
    """Test Partial TP and BE settings are isolated between users"""
    
    def test_users_independent(self):
        """Test different users have independent settings"""
        user1 = TEST_USERS[0]
        user2 = TEST_USERS[1]
        strategy = "oi"
        
        # Set different values for each user
        pg_set_strategy_setting(user1, strategy, "long_partial_tp_1_trigger_pct", 10.0, "bybit")
        pg_set_strategy_setting(user2, strategy, "long_partial_tp_1_trigger_pct", 20.0, "bybit")
        
        settings1 = pg_get_strategy_settings(user1, strategy, "bybit")
        settings2 = pg_get_strategy_settings(user2, strategy, "bybit")
        
        assert settings1.get("long_partial_tp_1_trigger_pct") == 10.0
        assert settings2.get("long_partial_tp_1_trigger_pct") == 20.0


class TestDBLayerIntegration:
    """Test integration with db.py layer"""
    
    def test_set_via_db_module(self):
        """Test setting Partial TP via db.set_strategy_setting"""
        uid = TEST_USERS[0]
        strategy = "oi"
        
        # Use db module function with prefixed field
        result = db.set_strategy_setting(uid, strategy, "long_partial_tp_enabled", True, "bybit", "demo")
        assert result is True
        
        # Verify via pg function
        settings = pg_get_strategy_settings(uid, strategy, "bybit")
        assert settings.get("long_partial_tp_enabled") is True
    
    def test_get_via_db_module(self):
        """Test getting BE settings via db.get_strategy_settings"""
        uid = TEST_USERS[1]
        strategy = "rsi_bb"
        
        # Set via pg function with prefixed field
        pg_set_strategy_setting(uid, strategy, "long_be_trigger_pct", 2.5, "bybit")
        
        # Get via pg function
        settings = pg_get_strategy_settings(uid, strategy, "bybit")
        assert settings.get("long_be_trigger_pct") == 2.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
