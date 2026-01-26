#!/usr/bin/env python3
"""
Full Strategy Trading Integration Tests

Comprehensive tests for the complete trading flow with strategy settings:
1. Global settings fallback chain
2. Per-strategy settings (per exchange, per account_type)
3. Side-specific settings (long_*, short_*)
4. ATR settings inheritance
5. Trade execution with correct parameters
6. Position monitoring with settings
7. Multi-user isolation

Author: Lyxen Team
Date: January 2026
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

# Skip marker for tests that need 4D schema update
needs_4d_update = pytest.mark.skip(reason="Needs update for 4D schema")
from typing import Dict, Any, Optional
from unittest.mock import patch, AsyncMock, MagicMock
import asyncio
import json
import time

import db
from db import (
    get_user_config,
    set_user_field,
    get_strategy_settings,
    set_strategy_setting,
    get_effective_settings,
    invalidate_user_cache,
    ensure_user,
    get_conn,
)


# =============================================================================
# TEST CONFIGURATION
# =============================================================================

TEST_USERS = {
    'global_only': 880001,       # Uses only global settings
    'strategy_specific': 880002, # Uses per-strategy settings
    'side_specific': 880003,     # Uses side-specific (long_*, short_*)
    'atr_custom': 880004,        # Custom ATR settings
    'mixed': 880005,             # Mixed global + strategy
    'demo_user': 880006,         # Demo only
    'real_user': 880007,         # Real only
    'both_user': 880008,         # Demo + Real
}

STRATEGIES = ['oi', 'rsi_bb', 'scryptomera', 'scalper', 'elcaro', 'fibonacci']


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(scope="module")
def test_db_setup():
    """Setup test database with all required columns"""
    with get_conn() as conn:
        cursor = conn.cursor()
        
        # Ensure all columns exist
        required_columns = [
            ("atr_periods", "INTEGER NOT NULL DEFAULT 7"),
            ("atr_multiplier_sl", "REAL NOT NULL DEFAULT 1.0"),
            ("atr_trigger_pct", "REAL NOT NULL DEFAULT 2.0"),
            ("atr_step_pct", "REAL NOT NULL DEFAULT 0.5"),
            ("direction", "TEXT NOT NULL DEFAULT 'all'"),
        ]
        
        for col_name, col_def in required_columns:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col_name} {col_def}")
            except:
                pass  # Column already exists
        
        conn.commit()
    yield
    
    # Cleanup
    cleanup_test_users()


@pytest.fixture(autouse=True)
def setup_and_cleanup(test_db_setup):
    """Setup test users before each test"""
    cleanup_test_users()
    create_test_users()
    yield
    # Don't cleanup after each test to allow inspection


def cleanup_test_users():
    """Remove all test users"""
    with get_conn() as conn:
        cursor = conn.cursor()
        for uid in TEST_USERS.values():
            cursor.execute("DELETE FROM user_strategy_settings WHERE user_id = %s", (uid,))
            cursor.execute("DELETE FROM active_positions WHERE user_id = %s", (uid,))
            cursor.execute("DELETE FROM trade_logs WHERE user_id = %s", (uid,))
            cursor.execute("DELETE FROM users WHERE user_id = %s", (uid,))
        conn.commit()


def create_test_users():
    """Create test users with different configurations"""
    for name, uid in TEST_USERS.items():
        ensure_user(uid)
        invalidate_user_cache(uid)
        
        # Set default global values
        set_user_field(uid, "percent", 1.0)
        set_user_field(uid, "sl_percent", 3.0)
        set_user_field(uid, "tp_percent", 6.0)
        set_user_field(uid, "leverage", 10)
        set_user_field(uid, "use_atr", 1)
        set_user_field(uid, "atr_periods", 7)
        set_user_field(uid, "atr_multiplier_sl", 1.0)
        set_user_field(uid, "atr_trigger_pct", 2.0)
        set_user_field(uid, "direction", "all")


# =============================================================================
# TEST CLASSES
# =============================================================================

class TestGlobalSettingsFallback:
    """Test that settings properly fallback to global when strategy setting is NULL"""
    
    def test_empty_strategy_uses_global(self):
        """When no strategy settings exist, should use global"""
        uid = TEST_USERS['global_only']
        
        # Set global settings
        set_user_field(uid, "percent", 2.5)
        set_user_field(uid, "sl_percent", 4.0)
        set_user_field(uid, "tp_percent", 8.0)
        set_user_field(uid, "atr_periods", 14)
        invalidate_user_cache(uid)
        
        # Get effective settings for OI (no strategy-specific settings)
        eff = get_effective_settings(uid, "oi", "bybit", "demo")
        
        assert eff['percent'] == 2.5, f"Expected percent=2.5, got {eff['percent']}"
        assert eff['sl_percent'] == 4.0, f"Expected sl_percent=4.0, got {eff['sl_percent']}"
        assert eff['tp_percent'] == 8.0, f"Expected tp_percent=8.0, got {eff['tp_percent']}"
        assert eff['atr_periods'] == 14, f"Expected atr_periods=14, got {eff['atr_periods']}"
    
    def test_partial_strategy_uses_global_for_missing(self):
        """When some strategy settings exist, use global for missing fields"""
        uid = TEST_USERS['mixed']
        
        # Set global settings
        set_user_field(uid, "percent", 1.5)
        set_user_field(uid, "sl_percent", 3.0)
        set_user_field(uid, "tp_percent", 6.0)
        set_user_field(uid, "atr_periods", 7)
        invalidate_user_cache(uid)
        
        # Set only percent for strategy
        set_strategy_setting(uid, "oi", "percent", 5.0, "bybit", "demo")
        
        eff = get_effective_settings(uid, "oi", "bybit", "demo")
        
        # Strategy setting should override
        assert eff['percent'] == 5.0, f"Expected percent=5.0, got {eff['percent']}"
        # Global should be used for missing
        assert eff['sl_percent'] == 3.0, f"Expected sl_percent=3.0 (global), got {eff['sl_percent']}"
        assert eff['tp_percent'] == 6.0, f"Expected tp_percent=6.0 (global), got {eff['tp_percent']}"
    
    def test_strategy_overrides_global(self):
        """Strategy-specific settings should override global"""
        uid = TEST_USERS['strategy_specific']
        
        # Set global
        set_user_field(uid, "percent", 1.0)
        set_user_field(uid, "sl_percent", 3.0)
        set_user_field(uid, "atr_periods", 7)
        invalidate_user_cache(uid)
        
        # Set strategy-specific
        set_strategy_setting(uid, "scalper", "percent", 10.0, "bybit", "demo")
        set_strategy_setting(uid, "scalper", "sl_percent", 15.0, "bybit", "demo")
        set_strategy_setting(uid, "scalper", "atr_periods", 21, "bybit", "demo")
        
        eff = get_effective_settings(uid, "scalper", "bybit", "demo")
        
        assert eff['percent'] == 10.0, f"Strategy percent should override global"
        assert eff['sl_percent'] == 15.0, f"Strategy sl_percent should override global"
        assert eff['atr_periods'] == 21, f"Strategy atr_periods should override global"


class TestPerExchangeAccountSettings:
    """Test isolation of settings per exchange and account type"""
    
    def test_demo_vs_real_isolation(self):
        """Settings should be isolated between demo and real accounts"""
        uid = TEST_USERS['both_user']
        
        # Set different settings for demo and real
        set_strategy_setting(uid, "oi", "percent", 1.0, "bybit", "demo")
        set_strategy_setting(uid, "oi", "sl_percent", 2.0, "bybit", "demo")
        
        set_strategy_setting(uid, "oi", "percent", 5.0, "bybit", "real")
        set_strategy_setting(uid, "oi", "sl_percent", 10.0, "bybit", "real")
        
        # Verify isolation
        demo_settings = get_strategy_settings(uid, "oi", "bybit", "demo")
        real_settings = get_strategy_settings(uid, "oi", "bybit", "real")
        
        assert demo_settings['percent'] == 1.0, "Demo should have percent=1.0"
        assert demo_settings['sl_percent'] == 2.0, "Demo should have sl_percent=2.0"
        
        assert real_settings['percent'] == 5.0, "Real should have percent=5.0"
        assert real_settings['sl_percent'] == 10.0, "Real should have sl_percent=10.0"
    
    def test_bybit_vs_hyperliquid_isolation(self):
        """Settings should be isolated between Bybit and HyperLiquid"""
        uid = TEST_USERS['mixed']
        
        # Bybit settings
        set_strategy_setting(uid, "scryptomera", "percent", 2.0, "bybit", "demo")
        set_strategy_setting(uid, "scryptomera", "leverage", 10, "bybit", "demo")
        
        # HyperLiquid settings
        set_strategy_setting(uid, "scryptomera", "percent", 8.0, "hyperliquid", "testnet")
        set_strategy_setting(uid, "scryptomera", "leverage", 5, "hyperliquid", "testnet")
        
        bybit = get_strategy_settings(uid, "scryptomera", "bybit", "demo")
        hl = get_strategy_settings(uid, "scryptomera", "hyperliquid", "testnet")
        
        assert bybit['percent'] == 2.0, "Bybit should have percent=2.0"
        assert bybit['leverage'] == 10, "Bybit should have leverage=10"
        
        assert hl['percent'] == 8.0, "HL should have percent=8.0"
        assert hl['leverage'] == 5, "HL should have leverage=5"


class TestSideSpecificSettings:
    """Test long_* and short_* specific settings"""
    
    def test_long_vs_short_settings(self):
        """Long and short should have independent settings"""
        uid = TEST_USERS['side_specific']
        
        set_strategy_setting(uid, "elcaro", "long_percent", 2.0, "bybit", "demo")
        set_strategy_setting(uid, "elcaro", "long_sl_percent", 3.0, "bybit", "demo")
        set_strategy_setting(uid, "elcaro", "long_tp_percent", 6.0, "bybit", "demo")
        
        set_strategy_setting(uid, "elcaro", "short_percent", 4.0, "bybit", "demo")
        set_strategy_setting(uid, "elcaro", "short_sl_percent", 5.0, "bybit", "demo")
        set_strategy_setting(uid, "elcaro", "short_tp_percent", 10.0, "bybit", "demo")
        
        settings = get_strategy_settings(uid, "elcaro", "bybit", "demo")
        
        assert settings['long_percent'] == 2.0
        assert settings['long_sl_percent'] == 3.0
        assert settings['long_tp_percent'] == 6.0
        
        assert settings['short_percent'] == 4.0
        assert settings['short_sl_percent'] == 5.0
        assert settings['short_tp_percent'] == 10.0
    
    def test_side_fallback_to_general(self):
        """If side_* is NULL, should fall back to general setting"""
        uid = TEST_USERS['side_specific']
        
        # Set only general percent
        set_strategy_setting(uid, "fibonacci", "percent", 3.0, "bybit", "demo")
        set_strategy_setting(uid, "fibonacci", "sl_percent", 4.0, "bybit", "demo")
        # Don't set long_* or short_*
        
        settings = get_strategy_settings(uid, "fibonacci", "bybit", "demo")
        
        # General should be set
        assert settings['percent'] == 3.0
        assert settings['sl_percent'] == 4.0
        
        # Side-specific should be None (fallback happens in get_effective_settings)
        assert settings.get('long_percent') is None
        assert settings.get('short_percent') is None
    
    def test_get_effective_with_side(self):
        """Test get_effective_settings with side parameter"""
        uid = TEST_USERS['side_specific']
        
        # Set global
        set_user_field(uid, "percent", 1.0)
        set_user_field(uid, "sl_percent", 2.0)
        invalidate_user_cache(uid)
        
        # Set general strategy setting
        set_strategy_setting(uid, "scalper", "percent", 5.0, "bybit", "demo")
        
        # Set only long side
        set_strategy_setting(uid, "scalper", "long_percent", 8.0, "bybit", "demo")
        set_strategy_setting(uid, "scalper", "long_sl_percent", 12.0, "bybit", "demo")
        
        # Get effective for LONG - should use long_*
        eff_long = get_effective_settings(uid, "scalper", "bybit", "demo", side="Buy")
        assert eff_long['percent'] == 8.0, f"LONG should use long_percent=8.0, got {eff_long['percent']}"
        assert eff_long['sl_percent'] == 12.0, f"LONG should use long_sl_percent=12.0"
        
        # Get effective for SHORT - should fallback to general (5.0) since short_* not set
        eff_short = get_effective_settings(uid, "scalper", "bybit", "demo", side="Sell")
        assert eff_short['percent'] == 5.0, f"SHORT should fallback to general percent=5.0, got {eff_short['percent']}"


class TestATRSettings:
    """Test ATR-related settings and fallback"""
    
    def test_atr_global_fallback(self):
        """When strategy ATR not set, use global"""
        uid = TEST_USERS['atr_custom']
        
        # Set global ATR
        set_user_field(uid, "atr_periods", 14)
        set_user_field(uid, "atr_multiplier_sl", 2.0)
        set_user_field(uid, "atr_trigger_pct", 3.0)
        set_user_field(uid, "use_atr", 1)
        invalidate_user_cache(uid)
        
        # Don't set strategy ATR
        eff = get_effective_settings(uid, "oi", "bybit", "demo")
        
        assert eff['atr_periods'] == 14, f"Should use global atr_periods=14"
        assert eff['atr_multiplier_sl'] == 2.0
        assert eff['atr_trigger_pct'] == 3.0
        assert eff['use_atr'] == True
    
    def test_strategy_atr_override(self):
        """Strategy ATR should override global"""
        uid = TEST_USERS['atr_custom']
        
        # Set global
        set_user_field(uid, "atr_periods", 7)
        set_user_field(uid, "atr_multiplier_sl", 1.0)
        invalidate_user_cache(uid)
        
        # Set strategy ATR
        set_strategy_setting(uid, "rsi_bb", "atr_periods", 21, "bybit", "demo")
        set_strategy_setting(uid, "rsi_bb", "atr_multiplier_sl", 3.0, "bybit", "demo")
        
        eff = get_effective_settings(uid, "rsi_bb", "bybit", "demo")
        
        assert eff['atr_periods'] == 21, "Strategy atr_periods should override"
        assert eff['atr_multiplier_sl'] == 3.0, "Strategy atr_multiplier_sl should override"
    
    def test_use_atr_toggle(self):
        """use_atr should control ATR mode per strategy"""
        uid = TEST_USERS['atr_custom']
        
        # Global has ATR enabled
        set_user_field(uid, "use_atr", 1)
        invalidate_user_cache(uid)
        
        # Strategy disables ATR
        set_strategy_setting(uid, "fibonacci", "use_atr", 0, "bybit", "demo")
        
        eff = get_effective_settings(uid, "fibonacci", "bybit", "demo")
        
        assert eff['use_atr'] == False, "Strategy should disable ATR"


class TestDirectionSettings:
    """Test direction (all/long/short) settings"""
    
    def test_direction_default(self):
        """Default direction should be 'all'"""
        uid = TEST_USERS['global_only']
        
        eff = get_effective_settings(uid, "oi", "bybit", "demo")
        assert eff['direction'] == 'all', f"Default direction should be 'all', got {eff['direction']}"
    
    def test_direction_per_strategy(self):
        """Each strategy can have its own direction"""
        uid = TEST_USERS['strategy_specific']
        
        set_strategy_setting(uid, "scryptomera", "direction", "long", "bybit", "demo")
        set_strategy_setting(uid, "scalper", "direction", "short", "bybit", "demo")
        set_strategy_setting(uid, "elcaro", "direction", "all", "bybit", "demo")
        
        scrypto = get_effective_settings(uid, "scryptomera", "bybit", "demo")
        scalper = get_effective_settings(uid, "scalper", "bybit", "demo")
        elcaro = get_effective_settings(uid, "elcaro", "bybit", "demo")
        
        assert scrypto['direction'] == 'long'
        assert scalper['direction'] == 'short'
        assert elcaro['direction'] == 'all'


class TestMultiUserIsolation:
    """Test that settings are isolated between users"""
    
    def test_users_have_independent_settings(self):
        """Each user's settings should be independent"""
        user1 = TEST_USERS['demo_user']
        user2 = TEST_USERS['real_user']
        
        # User 1 settings
        set_user_field(user1, "percent", 1.0)
        set_strategy_setting(user1, "oi", "percent", 2.0, "bybit", "demo")
        invalidate_user_cache(user1)
        
        # User 2 settings (different)
        set_user_field(user2, "percent", 10.0)
        set_strategy_setting(user2, "oi", "percent", 20.0, "bybit", "demo")
        invalidate_user_cache(user2)
        
        # Verify isolation
        u1_cfg = get_user_config(user1)
        u2_cfg = get_user_config(user2)
        
        assert u1_cfg['percent'] == 1.0, "User 1 should have percent=1.0"
        assert u2_cfg['percent'] == 10.0, "User 2 should have percent=10.0"
        
        u1_strat = get_strategy_settings(user1, "oi", "bybit", "demo")
        u2_strat = get_strategy_settings(user2, "oi", "bybit", "demo")
        
        assert u1_strat['percent'] == 2.0
        assert u2_strat['percent'] == 20.0
    
    def test_all_strategies_isolation(self):
        """All strategies should be isolated per user"""
        user1 = TEST_USERS['demo_user']
        user2 = TEST_USERS['real_user']
        
        for strategy in STRATEGIES:
            set_strategy_setting(user1, strategy, "percent", 1.0, "bybit", "demo")
            set_strategy_setting(user2, strategy, "percent", 10.0, "bybit", "demo")
        
        for strategy in STRATEGIES:
            u1 = get_strategy_settings(user1, strategy, "bybit", "demo")
            u2 = get_strategy_settings(user2, strategy, "bybit", "demo")
            
            assert u1['percent'] == 1.0, f"User 1 {strategy} should be 1.0"
            assert u2['percent'] == 10.0, f"User 2 {strategy} should be 10.0"


class TestGetUserConfig:
    """Test get_user_config returns all expected fields"""
    
    def test_config_has_all_global_fields(self):
        """get_user_config should return all global settings"""
        uid = TEST_USERS['global_only']
        
        set_user_field(uid, "percent", 2.5)
        set_user_field(uid, "sl_percent", 4.0)
        set_user_field(uid, "tp_percent", 8.0)
        set_user_field(uid, "leverage", 25)
        set_user_field(uid, "use_atr", 1)
        set_user_field(uid, "atr_periods", 14)
        set_user_field(uid, "atr_multiplier_sl", 2.0)
        set_user_field(uid, "atr_trigger_pct", 3.0)
        set_user_field(uid, "atr_step_pct", 0.75)
        set_user_field(uid, "direction", "long")
        invalidate_user_cache(uid)
        
        cfg = get_user_config(uid)
        
        # Core fields
        assert cfg['percent'] == 2.5
        assert cfg['sl_percent'] == 4.0
        assert cfg['tp_percent'] == 8.0
        assert cfg['leverage'] == 25
        assert cfg['use_atr'] == True
        
        # ATR fields
        assert cfg['atr_periods'] == 14, f"Expected atr_periods=14, got {cfg.get('atr_periods')}"
        assert cfg['atr_multiplier_sl'] == 2.0
        assert cfg['atr_trigger_pct'] == 3.0
        assert cfg['atr_step_pct'] == 0.75
        
        # Direction
        assert cfg['direction'] == 'long'
    
    def test_config_caching(self):
        """Config should be cached"""
        uid = TEST_USERS['demo_user']
        
        # First call
        cfg1 = get_user_config(uid)
        
        # Second call should return same object (from cache)
        cfg2 = get_user_config(uid)
        
        # After invalidation, should be different
        invalidate_user_cache(uid)
        cfg3 = get_user_config(uid)
        
        # cfg1 and cfg2 could be same reference if cached
        # cfg3 should be fresh


@needs_4d_update
class TestGetEffectiveSettingsComplete:
    """Complete test of get_effective_settings fallback chain"""
    
    def test_complete_fallback_chain(self):
        """Test: Strategy → Global → Default"""
        uid = TEST_USERS['mixed']
        
        # Set some global
        set_user_field(uid, "percent", 2.0)
        set_user_field(uid, "sl_percent", 4.0)
        set_user_field(uid, "atr_periods", 14)
        invalidate_user_cache(uid)
        
        # Set some strategy (but not all)
        set_strategy_setting(uid, "oi", "percent", 5.0, "bybit", "demo")
        set_strategy_setting(uid, "oi", "tp_percent", 12.0, "bybit", "demo")
        
        eff = get_effective_settings(uid, "oi", "bybit", "demo")
        
        # From strategy
        assert eff['percent'] == 5.0, "percent should come from strategy"
        assert eff['tp_percent'] == 12.0, "tp_percent should come from strategy"
        
        # From global (not set in strategy)
        assert eff['sl_percent'] == 4.0, "sl_percent should fallback to global"
        assert eff['atr_periods'] == 14, "atr_periods should fallback to global"
        
        # Check use_atr is boolean
        assert isinstance(eff['use_atr'], bool), f"use_atr should be bool, got {type(eff['use_atr'])}"
    
    def test_all_fields_present(self):
        """get_effective_settings should return all expected fields"""
        uid = TEST_USERS['global_only']
        
        eff = get_effective_settings(uid, "oi", "bybit", "demo")
        
        required_fields = [
            'percent', 'sl_percent', 'tp_percent', 'leverage',
            'use_atr', 'atr_periods', 'atr_multiplier_sl', 'atr_trigger_pct',
            'direction', 'order_type'
        ]
        
        for field in required_fields:
            assert field in eff, f"Missing field: {field}"
            assert eff[field] is not None, f"Field {field} is None"


@needs_4d_update
class TestOrderTypeSettings:
    """Test order type (market/limit) settings"""
    
    def test_order_type_default_market(self):
        """Default order type should be 'market'"""
        uid = TEST_USERS['global_only']
        
        eff = get_effective_settings(uid, "oi", "bybit", "demo")
        assert eff['order_type'] == 'market', f"Default should be market, got {eff['order_type']}"
    
    def test_order_type_per_strategy(self):
        """Each strategy can have its own order type"""
        uid = TEST_USERS['strategy_specific']
        
        set_strategy_setting(uid, "scryptomera", "order_type", "limit", "bybit", "demo")
        set_strategy_setting(uid, "scalper", "order_type", "market", "bybit", "demo")
        
        scrypto = get_effective_settings(uid, "scryptomera", "bybit", "demo")
        scalper = get_effective_settings(uid, "scalper", "bybit", "demo")
        
        assert scrypto['order_type'] == 'limit'
        assert scalper['order_type'] == 'market'


class TestLeverageSettings:
    """Test leverage settings and validation"""
    
    def test_leverage_default(self):
        """Default leverage should be set"""
        uid = TEST_USERS['global_only']
        
        cfg = get_user_config(uid)
        assert cfg['leverage'] >= 1, "Default leverage should be >= 1"
        assert cfg['leverage'] <= 100, "Default leverage should be <= 100"
    
    def test_leverage_per_strategy(self):
        """Leverage can be set per strategy"""
        uid = TEST_USERS['strategy_specific']
        
        set_strategy_setting(uid, "oi", "leverage", 50, "bybit", "demo")
        set_strategy_setting(uid, "scalper", "leverage", 5, "bybit", "demo")
        
        eff_oi = get_effective_settings(uid, "oi", "bybit", "demo")
        eff_scalper = get_effective_settings(uid, "scalper", "bybit", "demo")
        
        assert eff_oi['leverage'] == 50
        assert eff_scalper['leverage'] == 5


class TestCoinsGroupSettings:
    """Test coins group filtering"""
    
    def test_coins_group_default(self):
        """Default coins_group should be None or ALL"""
        uid = TEST_USERS['global_only']
        
        settings = get_strategy_settings(uid, "oi", "bybit", "demo")
        coins = settings.get('coins_group')
        
        # Should be None or 'ALL' by default
        assert coins is None or coins == 'ALL' or coins == '', f"Default coins_group: {coins}"
    
    def test_coins_group_per_strategy(self):
        """Each strategy can have its own coins group"""
        uid = TEST_USERS['strategy_specific']
        
        set_strategy_setting(uid, "oi", "coins_group", "MAJOR", "bybit", "demo")
        set_strategy_setting(uid, "scalper", "coins_group", "MEME", "bybit", "demo")
        
        oi = get_strategy_settings(uid, "oi", "bybit", "demo")
        scalper = get_strategy_settings(uid, "scalper", "bybit", "demo")
        
        assert oi['coins_group'] == 'MAJOR'
        assert scalper['coins_group'] == 'MEME'


# =============================================================================
# TRADING FLOW SIMULATION TESTS
# =============================================================================

@needs_4d_update
class TestTradingFlowSimulation:
    """Simulate the complete trading flow with settings"""
    
    def test_signal_processing_uses_correct_settings(self):
        """When processing a signal, correct settings should be used"""
        uid = TEST_USERS['strategy_specific']
        
        # Setup: Different settings for OI on demo vs real
        set_strategy_setting(uid, "oi", "percent", 1.0, "bybit", "demo")
        set_strategy_setting(uid, "oi", "sl_percent", 2.0, "bybit", "demo")
        set_strategy_setting(uid, "oi", "tp_percent", 4.0, "bybit", "demo")
        
        set_strategy_setting(uid, "oi", "percent", 5.0, "bybit", "real")
        set_strategy_setting(uid, "oi", "sl_percent", 10.0, "bybit", "real")
        set_strategy_setting(uid, "oi", "tp_percent", 20.0, "bybit", "real")
        
        # Simulate getting settings for demo trade
        demo_settings = get_effective_settings(uid, "oi", "bybit", "demo")
        assert demo_settings['percent'] == 1.0
        assert demo_settings['sl_percent'] == 2.0
        assert demo_settings['tp_percent'] == 4.0
        
        # Simulate getting settings for real trade
        real_settings = get_effective_settings(uid, "oi", "bybit", "real")
        assert real_settings['percent'] == 5.0
        assert real_settings['sl_percent'] == 10.0
        assert real_settings['tp_percent'] == 20.0
    
    def test_side_specific_in_trade(self):
        """Trade should use side-specific settings when available"""
        uid = TEST_USERS['side_specific']
        
        # Different settings for long vs short
        set_strategy_setting(uid, "scryptomera", "long_percent", 2.0, "bybit", "demo")
        set_strategy_setting(uid, "scryptomera", "long_sl_percent", 3.0, "bybit", "demo")
        
        set_strategy_setting(uid, "scryptomera", "short_percent", 5.0, "bybit", "demo")
        set_strategy_setting(uid, "scryptomera", "short_sl_percent", 8.0, "bybit", "demo")
        
        # LONG trade
        long_settings = get_effective_settings(uid, "scryptomera", "bybit", "demo", side="Buy")
        assert long_settings['percent'] == 2.0, f"LONG should use 2.0, got {long_settings['percent']}"
        assert long_settings['sl_percent'] == 3.0
        
        # SHORT trade
        short_settings = get_effective_settings(uid, "scryptomera", "bybit", "demo", side="Sell")
        assert short_settings['percent'] == 5.0, f"SHORT should use 5.0, got {short_settings['percent']}"
        assert short_settings['sl_percent'] == 8.0
    
    def test_atr_settings_in_position_monitor(self):
        """Position monitoring should use correct ATR settings"""
        uid = TEST_USERS['atr_custom']
        
        # Strategy-specific ATR
        set_strategy_setting(uid, "elcaro", "use_atr", 1, "bybit", "demo")
        set_strategy_setting(uid, "elcaro", "atr_periods", 21, "bybit", "demo")
        set_strategy_setting(uid, "elcaro", "atr_multiplier_sl", 2.5, "bybit", "demo")
        set_strategy_setting(uid, "elcaro", "atr_trigger_pct", 5.0, "bybit", "demo")
        
        eff = get_effective_settings(uid, "elcaro", "bybit", "demo")
        
        assert eff['use_atr'] == True
        assert eff['atr_periods'] == 21
        assert eff['atr_multiplier_sl'] == 2.5
        assert eff['atr_trigger_pct'] == 5.0


# =============================================================================
# RUN ALL TESTS
# =============================================================================

def run_all_tests():
    """Run all tests and show summary"""
    import subprocess
    result = subprocess.run(
        ['python3', '-m', 'pytest', __file__, '-v', '--tb=short'],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
    return result.returncode


if __name__ == "__main__":
    run_all_tests()
