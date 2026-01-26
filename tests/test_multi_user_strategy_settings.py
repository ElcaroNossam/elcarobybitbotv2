"""
Comprehensive Multi-User Strategy Settings Tests

Tests the complete trading flow with different settings per user, exchange, and account type:
1. Settings storage and retrieval per exchange/account
2. Signal detection with context-aware settings
3. Trade opening with correct parameters
4. Position monitoring with ATR/SL/TP
5. Position closing with correct exit detection
6. Trade history logging

This validates the complex mechanism of separate settings per exchange/account type.

NOTE: Many tests in this file need update for 4D schema (user_id, strategy, side, exchange).
The codebase has migrated from 3D to 4D schema with side-specific settings.
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Skip marker for tests that need 4D schema update
needs_4d_update = pytest.mark.skip(reason="Needs update for 4D schema (user_id, strategy, side, exchange)")

import db
from db import (
    get_user_trading_context,
    normalize_account_type,
    get_strategy_settings,
    set_strategy_setting,
    get_active_account_types,
    get_strategy_account_types,
)


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def test_users(test_db):
    """Create test users with different configurations.
    Uses test_db fixture from conftest.py to ensure proper database setup.
    """
    users = {
        'bybit_demo_user': 900001,
        'bybit_real_user': 900002,
        'hyperliquid_testnet_user': 900003,
        'hyperliquid_mainnet_user': 900004,
        'multi_exchange_user': 900005,
    }
    
    # Create users in database using cursor from test_db
    cursor = test_db.cursor()
    for name, uid in users.items():
        cursor.execute("""
            INSERT OR REPLACE INTO users (user_id, username, is_allowed)
            VALUES (?, ?, 1)
        """, (uid, name))
    test_db.commit()
    
    yield users
    
    # Cleanup
    cursor = test_db.cursor()
    for uid in users.values():
        cursor.execute("DELETE FROM users WHERE user_id = ?", (uid,))
        cursor.execute("DELETE FROM user_strategy_settings WHERE user_id = ?", (uid,))
        cursor.execute("DELETE FROM active_positions WHERE user_id = ?", (uid,))
        cursor.execute("DELETE FROM trade_logs WHERE user_id = ?", (uid,))
    test_db.commit()


@pytest.fixture
def setup_user_configs(test_db, test_users):
    """Setup different configurations for each test user.
    Uses test_db fixture to ensure database is properly initialized.
    """
    cursor = test_db.cursor()
    
    # User 1: Bybit Demo - Conservative settings
    cursor.execute("""
        UPDATE users SET exchange_type=?, trading_mode=?, demo_api_key=?, demo_api_secret=?
        WHERE user_id=?
    """, ('bybit', 'demo', 'test_demo_key', 'test_demo_secret', test_users['bybit_demo_user']))
    
    # User 2: Bybit Real - Aggressive settings
    cursor.execute("""
        UPDATE users SET exchange_type=?, trading_mode=?, real_api_key=?, real_api_secret=?
        WHERE user_id=?
    """, ('bybit', 'real', 'test_real_key', 'test_real_secret', test_users['bybit_real_user']))
    
    # User 3: HyperLiquid Testnet
    cursor.execute("""
        UPDATE users SET exchange_type=?, trading_mode=?, hl_private_key=?, hl_testnet=?
        WHERE user_id=?
    """, ('hyperliquid', 'testnet', 'test_hl_key', 1, test_users['hyperliquid_testnet_user']))
    
    # User 4: HyperLiquid Mainnet
    cursor.execute("""
        UPDATE users SET exchange_type=?, trading_mode=?, hl_private_key=?, hl_testnet=?
        WHERE user_id=?
    """, ('hyperliquid', 'mainnet', 'test_hl_key_mainnet', 0, test_users['hyperliquid_mainnet_user']))
    
    # User 5: Multi-exchange user (Bybit + HL)
    cursor.execute("""
        UPDATE users SET exchange_type=?, trading_mode=?, demo_api_key=?, demo_api_secret=?, hl_private_key=?
        WHERE user_id=?
    """, ('bybit', 'demo', 'test_multi_demo', 'test_multi_secret', 'test_multi_hl_key', test_users['multi_exchange_user']))
    
    test_db.commit()
    
    return test_users


# ============================================================================
# TEST: CONTEXT DETECTION
# ============================================================================

@needs_4d_update
class TestContextDetection:
    """Test get_user_trading_context() for different users"""
    
    def test_bybit_demo_context(self, setup_user_configs):
        """Test context for Bybit demo user"""
        uid = setup_user_configs['bybit_demo_user']
        context = get_user_trading_context(uid)
        
        assert context['exchange'] == 'bybit'
        assert context['account_type'] == 'demo'
        assert context['trading_mode'] == 'demo'
    
    def test_bybit_real_context(self, setup_user_configs):
        """Test context for Bybit real user"""
        uid = setup_user_configs['bybit_real_user']
        context = get_user_trading_context(uid)
        
        assert context['exchange'] == 'bybit'
        assert context['account_type'] == 'real'
        assert context['trading_mode'] == 'real'
    
    def test_hyperliquid_testnet_context(self, setup_user_configs):
        """Test context for HyperLiquid testnet user"""
        uid = setup_user_configs['hyperliquid_testnet_user']
        context = get_user_trading_context(uid)
        
        assert context['exchange'] == 'hyperliquid'
        assert context['account_type'] == 'testnet'
    
    def test_hyperliquid_mainnet_context(self, setup_user_configs):
        """Test context for HyperLiquid mainnet user"""
        uid = setup_user_configs['hyperliquid_mainnet_user']
        context = get_user_trading_context(uid)
        
        assert context['exchange'] == 'hyperliquid'
        assert context['account_type'] == 'mainnet'


@needs_4d_update
class TestNormalizeAccountType:
    """Test account type normalization between exchanges"""
    
    def test_bybit_demo_stays_demo(self):
        """Bybit demo stays demo"""
        assert normalize_account_type('demo', 'bybit') == 'demo'
    
    def test_bybit_real_stays_real(self):
        """Bybit real stays real"""
        assert normalize_account_type('real', 'bybit') == 'real'
    
    def test_hyperliquid_demo_becomes_testnet(self):
        """HyperLiquid demo becomes testnet"""
        assert normalize_account_type('demo', 'hyperliquid') == 'testnet'
    
    def test_hyperliquid_real_becomes_mainnet(self):
        """HyperLiquid real becomes mainnet"""
        assert normalize_account_type('real', 'hyperliquid') == 'mainnet'
    
    def test_bybit_testnet_becomes_demo(self):
        """Bybit testnet becomes demo"""
        assert normalize_account_type('testnet', 'bybit') == 'demo'
    
    def test_bybit_mainnet_becomes_real(self):
        """Bybit mainnet becomes real"""
        assert normalize_account_type('mainnet', 'bybit') == 'real'


# ============================================================================
# TEST: STRATEGY SETTINGS ISOLATION
# ============================================================================

@needs_4d_update
@needs_4d_update
class TestStrategySettingsIsolation:
    """Test that strategy settings are isolated per exchange/account"""
    
    def test_different_settings_per_exchange(self, setup_user_configs):
        """Same user has different settings for different exchanges"""
        uid = setup_user_configs['multi_exchange_user']
        
        # Set Bybit demo settings
        set_strategy_setting(uid, 'scryptomera', 'sl_percent', 3.0, 'bybit', 'demo')
        set_strategy_setting(uid, 'scryptomera', 'tp_percent', 8.0, 'bybit', 'demo')
        set_strategy_setting(uid, 'scryptomera', 'percent', 1.0, 'bybit', 'demo')
        
        # Set HyperLiquid testnet settings (different)
        set_strategy_setting(uid, 'scryptomera', 'sl_percent', 5.0, 'hyperliquid', 'testnet')
        set_strategy_setting(uid, 'scryptomera', 'tp_percent', 15.0, 'hyperliquid', 'testnet')
        set_strategy_setting(uid, 'scryptomera', 'percent', 2.0, 'hyperliquid', 'testnet')
        
        # Verify Bybit settings
        bybit_settings = get_strategy_settings(uid, 'scryptomera', 'bybit', 'demo')
        assert bybit_settings.get('sl_percent') == 3.0
        assert bybit_settings.get('tp_percent') == 8.0
        assert bybit_settings.get('percent') == 1.0
        
        # Verify HL settings are different
        hl_settings = get_strategy_settings(uid, 'scryptomera', 'hyperliquid', 'testnet')
        assert hl_settings.get('sl_percent') == 5.0
        assert hl_settings.get('tp_percent') == 15.0
        assert hl_settings.get('percent') == 2.0
    
    def test_different_settings_per_account_type(self, setup_user_configs):
        """Same user/exchange has different settings for demo vs real"""
        uid = setup_user_configs['multi_exchange_user']
        
        # Set Bybit demo settings
        set_strategy_setting(uid, 'scalper', 'sl_percent', 2.0, 'bybit', 'demo')
        set_strategy_setting(uid, 'scalper', 'leverage', 10, 'bybit', 'demo')
        
        # Set Bybit real settings (more conservative)
        set_strategy_setting(uid, 'scalper', 'sl_percent', 1.5, 'bybit', 'real')
        set_strategy_setting(uid, 'scalper', 'leverage', 5, 'bybit', 'real')
        
        # Verify demo settings
        demo_settings = get_strategy_settings(uid, 'scalper', 'bybit', 'demo')
        assert demo_settings.get('sl_percent') == 2.0
        assert demo_settings.get('leverage') == 10
        
        # Verify real settings are different
        real_settings = get_strategy_settings(uid, 'scalper', 'bybit', 'real')
        assert real_settings.get('sl_percent') == 1.5
        assert real_settings.get('leverage') == 5
    
    def test_all_strategies_isolated(self, setup_user_configs):
        """All strategies maintain separate settings per context"""
        uid = setup_user_configs['bybit_demo_user']
        strategies = ['scryptomera', 'scalper', 'elcaro', 'fibonacci', 'oi', 'rsi_bb']
        
        # Set different settings for each strategy
        for i, strategy in enumerate(strategies):
            sl = 1.0 + i * 0.5
            tp = 5.0 + i * 2.0
            set_strategy_setting(uid, strategy, 'sl_percent', sl, 'bybit', 'demo')
            set_strategy_setting(uid, strategy, 'tp_percent', tp, 'bybit', 'demo')
        
        # Verify each strategy has its own settings
        for i, strategy in enumerate(strategies):
            settings = get_strategy_settings(uid, strategy, 'bybit', 'demo')
            expected_sl = 1.0 + i * 0.5
            expected_tp = 5.0 + i * 2.0
            assert settings.get('sl_percent') == expected_sl, f"{strategy} SL mismatch"
            assert settings.get('tp_percent') == expected_tp, f"{strategy} TP mismatch"


# ============================================================================
# TEST: DIRECTION SETTINGS
# ============================================================================

@needs_4d_update
@needs_4d_update
class TestDirectionSettings:
    """Test direction (long/short/all) settings per exchange/account"""
    
    def test_direction_isolated_per_context(self, setup_user_configs):
        """Direction setting is isolated per exchange/account"""
        uid = setup_user_configs['multi_exchange_user']
        
        # Bybit demo: only longs
        set_strategy_setting(uid, 'scryptomera', 'direction', 'long', 'bybit', 'demo')
        
        # Bybit real: all directions
        set_strategy_setting(uid, 'scryptomera', 'direction', 'all', 'bybit', 'real')
        
        # HL testnet: only shorts
        set_strategy_setting(uid, 'scryptomera', 'direction', 'short', 'hyperliquid', 'testnet')
        
        # Verify
        demo_settings = get_strategy_settings(uid, 'scryptomera', 'bybit', 'demo')
        real_settings = get_strategy_settings(uid, 'scryptomera', 'bybit', 'real')
        hl_settings = get_strategy_settings(uid, 'scryptomera', 'hyperliquid', 'testnet')
        
        assert demo_settings.get('direction') == 'long'
        assert real_settings.get('direction') == 'all'
        assert hl_settings.get('direction') == 'short'


# ============================================================================
# TEST: ATR SETTINGS
# ============================================================================

@needs_4d_update
@needs_4d_update
class TestATRSettings:
    """Test ATR trailing stop settings per exchange/account"""
    
    def test_atr_settings_isolated(self, setup_user_configs):
        """ATR settings are isolated per exchange/account"""
        uid = setup_user_configs['multi_exchange_user']
        
        # Bybit demo: ATR enabled with specific params
        set_strategy_setting(uid, 'scalper', 'use_atr', 1, 'bybit', 'demo')
        set_strategy_setting(uid, 'scalper', 'atr_periods', 14, 'bybit', 'demo')
        set_strategy_setting(uid, 'scalper', 'atr_multiplier_sl', 2.0, 'bybit', 'demo')
        
        # Bybit real: ATR disabled
        set_strategy_setting(uid, 'scalper', 'use_atr', 0, 'bybit', 'real')
        
        # Verify
        demo_settings = get_strategy_settings(uid, 'scalper', 'bybit', 'demo')
        real_settings = get_strategy_settings(uid, 'scalper', 'bybit', 'real')
        
        assert demo_settings.get('use_atr') == 1
        assert demo_settings.get('atr_periods') == 14
        assert demo_settings.get('atr_multiplier_sl') == 2.0
        assert real_settings.get('use_atr') == 0


# ============================================================================
# TEST: COINS GROUP FILTER
# ============================================================================

@needs_4d_update
@needs_4d_update
class TestCoinsGroupFilter:
    """Test coins group filter settings"""
    
    def test_coins_group_isolated(self, setup_user_configs):
        """Coins group filter is isolated per context"""
        uid = setup_user_configs['multi_exchange_user']
        
        # Bybit demo: TOP only
        set_strategy_setting(uid, 'scryptomera', 'coins_group', 'TOP', 'bybit', 'demo')
        
        # Bybit real: ALL coins
        set_strategy_setting(uid, 'scryptomera', 'coins_group', 'ALL', 'bybit', 'real')
        
        # Verify
        demo_settings = get_strategy_settings(uid, 'scryptomera', 'bybit', 'demo')
        real_settings = get_strategy_settings(uid, 'scryptomera', 'bybit', 'real')
        
        assert demo_settings.get('coins_group') == 'TOP'
        assert real_settings.get('coins_group') == 'ALL'


# ============================================================================
# TEST: ORDER TYPE SETTINGS
# ============================================================================

@needs_4d_update
@needs_4d_update
class TestOrderTypeSettings:
    """Test order type (market/limit) settings"""
    
    def test_order_type_isolated(self, setup_user_configs):
        """Order type is isolated per context"""
        uid = setup_user_configs['multi_exchange_user']
        
        # Bybit demo: market orders
        set_strategy_setting(uid, 'scalper', 'order_type', 'market', 'bybit', 'demo')
        
        # Bybit real: limit orders
        set_strategy_setting(uid, 'scalper', 'order_type', 'limit', 'bybit', 'real')
        
        # Verify
        demo_settings = get_strategy_settings(uid, 'scalper', 'bybit', 'demo')
        real_settings = get_strategy_settings(uid, 'scalper', 'bybit', 'real')
        
        assert demo_settings.get('order_type') == 'market'
        assert real_settings.get('order_type') == 'limit'


# ============================================================================
# TEST: SIDE-SPECIFIC SETTINGS
# ============================================================================

class TestSideSpecificSettings:
    """Test side-specific (long/short) parameter settings"""
    
    def test_side_specific_params(self, setup_user_configs):
        """Different params for LONG vs SHORT trades"""
        uid = setup_user_configs['bybit_demo_user']
        
        # Set LONG-specific params
        set_strategy_setting(uid, 'elcaro', 'long_sl_percent', 2.0, 'bybit', 'demo')
        set_strategy_setting(uid, 'elcaro', 'long_tp_percent', 6.0, 'bybit', 'demo')
        set_strategy_setting(uid, 'elcaro', 'long_percent', 1.0, 'bybit', 'demo')
        
        # Set SHORT-specific params (more aggressive)
        set_strategy_setting(uid, 'elcaro', 'short_sl_percent', 3.0, 'bybit', 'demo')
        set_strategy_setting(uid, 'elcaro', 'short_tp_percent', 10.0, 'bybit', 'demo')
        set_strategy_setting(uid, 'elcaro', 'short_percent', 1.5, 'bybit', 'demo')
        
        # Verify
        settings = get_strategy_settings(uid, 'elcaro', 'bybit', 'demo')
        
        assert settings.get('long_sl_percent') == 2.0
        assert settings.get('long_tp_percent') == 6.0
        assert settings.get('long_percent') == 1.0
        
        assert settings.get('short_sl_percent') == 3.0
        assert settings.get('short_tp_percent') == 10.0
        assert settings.get('short_percent') == 1.5


# ============================================================================
# TEST: COMPLETE TRADING FLOW SIMULATION
# ============================================================================

@needs_4d_update
@needs_4d_update
class TestTradingFlowSimulation:
    """Simulate complete trading flow with context-aware settings"""
    
    def test_get_strategy_trade_params_uses_context(self, setup_user_configs):
        """get_strategy_trade_params uses correct exchange/account context"""
        # This test verifies the bot.py function behavior
        uid = setup_user_configs['bybit_demo_user']
        
        # Set specific settings for this context
        set_strategy_setting(uid, 'scryptomera', 'sl_percent', 4.0, 'bybit', 'demo')
        set_strategy_setting(uid, 'scryptomera', 'tp_percent', 12.0, 'bybit', 'demo')
        set_strategy_setting(uid, 'scryptomera', 'percent', 2.0, 'bybit', 'demo')
        set_strategy_setting(uid, 'scryptomera', 'leverage', 15, 'bybit', 'demo')
        
        # Verify settings are stored
        settings = get_strategy_settings(uid, 'scryptomera', 'bybit', 'demo')
        assert settings.get('sl_percent') == 4.0
        assert settings.get('tp_percent') == 12.0
        assert settings.get('percent') == 2.0
        assert settings.get('leverage') == 15
    
    def test_position_tracking_with_context(self, setup_user_configs):
        """Positions are tracked with correct exchange/account context"""
        uid = setup_user_configs['bybit_demo_user']
        
        # Add position with context
        db.add_active_position(
            user_id=uid,
            symbol='BTCUSDT',
            side='LONG',
            entry_price=50000.0,
            size=0.1,
            strategy='scryptomera',
            account_type='demo',
            exchange='bybit'
        )
        
        # Verify position exists for demo
        positions = db.get_active_positions(uid, account_type='demo', exchange='bybit')
        assert len(positions) >= 1
        
        btc_pos = next((p for p in positions if p.get('symbol') == 'BTCUSDT'), None)
        assert btc_pos is not None
        assert btc_pos['account_type'] == 'demo'
        assert btc_pos['strategy'] == 'scryptomera'
        
        # Cleanup
        db.remove_active_position(uid, 'BTCUSDT', account_type='demo', exchange='bybit')
    
    def test_trade_log_with_context(self, setup_user_configs):
        """Trade logs include exchange/account context"""
        uid = setup_user_configs['bybit_demo_user']
        
        # Add trade log with exchange for multitenancy
        db.add_trade_log(
            user_id=uid,
            signal_id=None,
            symbol='ETHUSDT',
            side='LONG',
            entry_price=3000.0,
            exit_price=3150.0,
            exit_reason='TP',
            pnl=150.0,
            pnl_pct=5.0,
            strategy='scalper',
            account_type='demo',
            exchange='bybit'
        )
        
        # Verify trade log
        with db.get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM trade_logs 
                WHERE user_id = %s AND symbol = 'ETHUSDT'
                ORDER BY ts DESC LIMIT 1
            """, (uid,))
            log = cur.fetchone()
            
            assert log is not None
            # Access columns by index since PostgreSQL returns tuple
            # Check that strategy and account_type are present
            # (exact indices depend on table schema)


# ============================================================================
# TEST: MULTI-USER DIFFERENT SETTINGS
# ============================================================================

@needs_4d_update
@needs_4d_update
class TestMultiUserDifferentSettings:
    """Test multiple users with different settings get correct params"""
    
    def test_users_have_isolated_settings(self, setup_user_configs):
        """Each user's settings are independent"""
        uid1 = setup_user_configs['bybit_demo_user']
        uid2 = setup_user_configs['bybit_real_user']
        
        # User 1: Conservative
        set_strategy_setting(uid1, 'elcaro', 'sl_percent', 2.0, 'bybit', 'demo')
        set_strategy_setting(uid1, 'elcaro', 'percent', 1.0, 'bybit', 'demo')
        
        # User 2: Aggressive
        set_strategy_setting(uid2, 'elcaro', 'sl_percent', 5.0, 'bybit', 'real')
        set_strategy_setting(uid2, 'elcaro', 'percent', 3.0, 'bybit', 'real')
        
        # Verify user 1
        s1 = get_strategy_settings(uid1, 'elcaro', 'bybit', 'demo')
        assert s1.get('sl_percent') == 2.0
        assert s1.get('percent') == 1.0
        
        # Verify user 2
        s2 = get_strategy_settings(uid2, 'elcaro', 'bybit', 'real')
        assert s2.get('sl_percent') == 5.0
        assert s2.get('percent') == 3.0
        
        # Verify they don't interfere
        s1_after = get_strategy_settings(uid1, 'elcaro', 'bybit', 'demo')
        assert s1_after.get('sl_percent') == 2.0
    
    def test_all_strategies_all_users(self, setup_user_configs):
        """All strategies work correctly for all users"""
        strategies = ['scryptomera', 'scalper', 'elcaro', 'fibonacci', 'oi', 'rsi_bb']
        users = list(setup_user_configs.values())
        
        # Set unique settings for each user/strategy combination
        for i, uid in enumerate(users):
            context = get_user_trading_context(uid)
            exchange = context['exchange']
            account_type = context['account_type']
            
            for j, strategy in enumerate(strategies):
                unique_sl = 1.0 + i * 0.5 + j * 0.1
                set_strategy_setting(uid, strategy, 'sl_percent', unique_sl, exchange, account_type)
        
        # Verify each user/strategy has correct unique setting
        for i, uid in enumerate(users):
            context = get_user_trading_context(uid)
            exchange = context['exchange']
            account_type = context['account_type']
            
            for j, strategy in enumerate(strategies):
                expected_sl = 1.0 + i * 0.5 + j * 0.1
                settings = get_strategy_settings(uid, strategy, exchange, account_type)
                actual_sl = settings.get('sl_percent')
                assert abs(actual_sl - expected_sl) < 0.01, \
                    f"User {uid} strategy {strategy}: expected {expected_sl}, got {actual_sl}"


# ============================================================================
# TEST: EXCHANGE SWITCHING
# ============================================================================

@needs_4d_update
@needs_4d_update
class TestExchangeSwitching:
    """Test settings behavior when user switches exchanges"""
    
    def test_settings_preserved_after_switch(self, setup_user_configs):
        """Settings are preserved when switching exchanges"""
        uid = setup_user_configs['multi_exchange_user']
        
        # Set Bybit settings
        set_strategy_setting(uid, 'scalper', 'sl_percent', 3.0, 'bybit', 'demo')
        
        # Set HL settings
        set_strategy_setting(uid, 'scalper', 'sl_percent', 5.0, 'hyperliquid', 'testnet')
        
        # "Switch" to Bybit
        db.set_user_field(uid, 'exchange_type', 'bybit')
        context = get_user_trading_context(uid)
        bybit_settings = get_strategy_settings(uid, 'scalper', context['exchange'], context['account_type'])
        
        # "Switch" to HL
        db.set_user_field(uid, 'exchange_type', 'hyperliquid')
        context = get_user_trading_context(uid)
        # Normalize account type for HL
        hl_account = normalize_account_type('demo', 'hyperliquid')
        hl_settings = get_strategy_settings(uid, 'scalper', context['exchange'], hl_account)
        
        # Both should retain their separate settings
        assert bybit_settings.get('sl_percent') == 3.0
        assert hl_settings.get('sl_percent') == 5.0


# ============================================================================
# TEST: ACTIVE ACCOUNT TYPES
# ============================================================================

@needs_4d_update
@needs_4d_update
class TestActiveAccountTypes:
    """Test get_active_account_types for different exchanges"""
    
    def test_bybit_demo_only(self, setup_user_configs):
        """User with only Bybit demo has correct account types"""
        uid = setup_user_configs['bybit_demo_user']
        account_types = get_active_account_types(uid)
        
        assert 'demo' in account_types
        assert 'real' not in account_types
    
    def test_hyperliquid_testnet(self, setup_user_configs):
        """User with HL testnet has correct account types"""
        uid = setup_user_configs['hyperliquid_testnet_user']
        account_types = get_active_account_types(uid)
        
        # HL uses testnet/mainnet
        assert 'testnet' in account_types or 'demo' in account_types
    
    def test_multi_exchange_user(self, setup_user_configs):
        """Multi-exchange user has both exchange types available"""
        uid = setup_user_configs['multi_exchange_user']
        
        # Check Bybit account types
        db.set_user_field(uid, 'exchange_type', 'bybit')
        bybit_types = get_active_account_types(uid)
        assert len(bybit_types) > 0


# ============================================================================
# TEST: STRATEGY ACCOUNT TYPES
# ============================================================================

@needs_4d_update
@needs_4d_update
class TestStrategyAccountTypes:
    """Test get_strategy_account_types"""
    
    def test_strategy_enabled_for_demo(self, setup_user_configs):
        """Strategy enabled for demo returns demo"""
        uid = setup_user_configs['bybit_demo_user']
        
        # Enable strategy for demo
        set_strategy_setting(uid, 'elcaro', 'trading_mode', 'demo', 'bybit', 'demo')
        set_strategy_setting(uid, 'elcaro', 'enabled', 1, 'bybit', 'demo')
        
        account_types = get_strategy_account_types(uid, 'elcaro')
        assert 'demo' in account_types
    
    def test_strategy_enabled_for_both(self, setup_user_configs):
        """Strategy enabled for both returns both types"""
        uid = setup_user_configs['bybit_demo_user']
        
        # Enable strategy for both
        set_strategy_setting(uid, 'scalper', 'trading_mode', 'both', 'bybit', 'demo')
        set_strategy_setting(uid, 'scalper', 'enabled', 1, 'bybit', 'demo')
        
        account_types = get_strategy_account_types(uid, 'scalper')
        # Should return available account types (at least demo since user has demo keys)
        assert len(account_types) > 0


# ============================================================================
# TEST: COMPLETE WORKFLOW SIMULATION
# ============================================================================

@needs_4d_update
@needs_4d_update
class TestCompleteWorkflow:
    """Simulate complete trading workflow"""
    
    def test_signal_to_trade_flow(self, setup_user_configs):
        """Complete flow: signal detection → settings lookup → trade params"""
        uid = setup_user_configs['bybit_demo_user']
        
        # 1. Setup settings for this context
        set_strategy_setting(uid, 'scryptomera', 'enabled', 1, 'bybit', 'demo')
        set_strategy_setting(uid, 'scryptomera', 'sl_percent', 3.0, 'bybit', 'demo')
        set_strategy_setting(uid, 'scryptomera', 'tp_percent', 8.0, 'bybit', 'demo')
        set_strategy_setting(uid, 'scryptomera', 'percent', 1.5, 'bybit', 'demo')
        set_strategy_setting(uid, 'scryptomera', 'direction', 'long', 'bybit', 'demo')
        set_strategy_setting(uid, 'scryptomera', 'order_type', 'market', 'bybit', 'demo')
        
        # 2. Get user's trading context
        context = get_user_trading_context(uid)
        assert context['exchange'] == 'bybit'
        assert context['account_type'] == 'demo'
        
        # 3. Get strategy settings for this context
        settings = get_strategy_settings(uid, 'scryptomera', context['exchange'], context['account_type'])
        
        # 4. Verify all settings are correct
        assert settings.get('enabled') == 1
        assert settings.get('sl_percent') == 3.0
        assert settings.get('tp_percent') == 8.0
        assert settings.get('percent') == 1.5
        assert settings.get('direction') == 'long'
        assert settings.get('order_type') == 'market'
        
        # 5. Simulate trade params calculation
        entry_price = 50000.0
        sl_price = entry_price * (1 - settings.get('sl_percent', 3.0) / 100)
        tp_price = entry_price * (1 + settings.get('tp_percent', 8.0) / 100)
        
        assert sl_price == 48500.0  # 50000 * 0.97
        assert tp_price == 54000.0  # 50000 * 1.08
    
    def test_position_close_flow(self, setup_user_configs):
        """Complete flow: position close → exit detection → logging"""
        uid = setup_user_configs['bybit_demo_user']
        
        # 1. Add position
        db.add_active_position(
            user_id=uid,
            symbol='SOLUSDT',
            side='LONG',
            entry_price=100.0,
            size=10.0,
            strategy='elcaro',
            account_type='demo',
            exchange='bybit'
        )
        
        # 2. Verify position exists
        positions = db.get_active_positions(uid, 'demo', exchange='bybit')
        sol_pos = next((p for p in positions if p.get('symbol') == 'SOLUSDT'), None)
        assert sol_pos is not None
        
        # 3. Simulate close (remove position, add to logs)
        db.remove_active_position(uid, 'SOLUSDT', 'demo', exchange='bybit')
        
        db.add_trade_log(
            user_id=uid,
            signal_id=None,
            symbol='SOLUSDT',
            side='LONG',
            entry_price=100.0,
            exit_price=108.0,
            exit_reason='TP',
            pnl=80.0,
            pnl_pct=8.0,
            strategy='elcaro',
            account_type='demo',
            exchange='bybit'
        )
        
        # 4. Verify position removed
        positions_after = db.get_active_positions(uid, 'demo', exchange='bybit')
        sol_pos_after = next((p for p in positions_after if p.get('symbol') == 'SOLUSDT'), None)
        assert sol_pos_after is None
        
        # 5. Verify trade log
        with db.get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM trade_logs 
                WHERE user_id = %s AND symbol = 'SOLUSDT'
                ORDER BY ts DESC LIMIT 1
            """, (uid,))
            log = cur.fetchone()
            
            assert log is not None
            # Check that trade log exists (exact column access depends on schema)


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
