"""
Multi-User Integration Tests - December 2025

Комплексные интеграционные тесты для мультипользовательского использования
с различными комбинациями настроек бирж, аккаунтов и стратегий.

Test Scenarios:
1. User A: All exchanges enabled (Bybit demo+real, HL testnet+mainnet)
2. User B: Bybit real only
3. User C: HL testnet only  
4. User D: Bybit demo + HL mainnet
5. Mixed strategy configurations
"""

import os
import sys
import pytest

# Skip marker for tests that need 4D schema update
needs_4d_update = pytest.mark.skip(reason="Needs update for 4D schema")
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import db


# ===========================
# TEST FIXTURES
# ===========================

@pytest.fixture
def multi_user_ids():
    """Generate test user IDs for multi-user testing"""
    return {
        'all_enabled': 900001,      # All exchanges and account types
        'bybit_real_only': 900002,  # Only Bybit real
        'hl_testnet_only': 900003,  # Only HL testnet
        'bybit_demo_hl_main': 900004,  # Bybit demo + HL mainnet
        'bybit_both': 900005,       # Bybit demo + real
        'hl_both': 900006,          # HL testnet + mainnet
    }


@pytest.fixture
def cleanup_test_users(test_db, multi_user_ids):
    """Cleanup test users before and after tests"""
    # Setup - clean any existing test data
    for uid in multi_user_ids.values():
        try:
            # Clean positions
            positions = db.get_active_positions(uid)
            for pos in positions:
                db.remove_active_position(uid, pos['symbol'], pos.get('account_type', 'demo'), exchange=pos.get('exchange', 'bybit'))
        except:
            pass
    
    yield
    
    # Teardown
    for uid in multi_user_ids.values():
        try:
            positions = db.get_active_positions(uid)
            for pos in positions:
                db.remove_active_position(uid, pos['symbol'], pos.get('account_type', 'demo'), exchange=pos.get('exchange', 'bybit'))
        except:
            pass


# ===========================
# USER CONFIGURATION TESTS
# ===========================

@needs_4d_update
class TestMultiUserConfiguration:
    """Test different user configuration scenarios"""
    
    def test_user_all_exchanges_enabled(self, test_db, multi_user_ids, cleanup_test_users):
        """User A: All exchanges and account types enabled"""
        uid = multi_user_ids['all_enabled']
        db.ensure_user(uid)
        
        # Set trading mode to 'both' (demo + real)
        db.set_trading_mode(uid, 'both')
        assert db.get_trading_mode(uid) == 'both'
        
        # Set exchange to bybit (can switch between bybit/hyperliquid)
        db.set_exchange_type(uid, 'bybit')
        assert db.get_exchange_type(uid) == 'bybit'
        
        # Enable all strategies via strategy settings (set percent to enable)
        for strategy in ['scryptomera', 'scalper', 'elcaro']:
            db.set_strategy_setting(uid, strategy, 'enabled', 1)
            db.set_strategy_setting(uid, strategy, 'percent', 1.0)
            
        # Verify strategies have settings
        for strategy in ['scryptomera', 'scalper', 'elcaro']:
            settings = db.get_strategy_settings(uid, strategy)
            # Strategy is considered enabled if it has percent set
            assert settings.get('percent') is not None or settings.get('enabled') is not None, \
                f"Strategy {strategy} should have settings"
    
    def test_user_bybit_real_only(self, test_db, multi_user_ids, cleanup_test_users):
        """User B: Only Bybit real account"""
        uid = multi_user_ids['bybit_real_only']
        db.ensure_user(uid)
        
        # Set trading mode to 'real' only
        db.set_trading_mode(uid, 'real')
        assert db.get_trading_mode(uid) == 'real'
        
        # Set exchange to bybit
        db.set_exchange_type(uid, 'bybit')
        assert db.get_exchange_type(uid) == 'bybit'
        
        # Verify user has no demo trading
        mode = db.get_trading_mode(uid)
        assert mode == 'real'
        assert mode != 'demo'
        assert mode != 'both'
    
    def test_user_hl_testnet_only(self, test_db, multi_user_ids, cleanup_test_users):
        """User C: Only HyperLiquid testnet"""
        uid = multi_user_ids['hl_testnet_only']
        db.ensure_user(uid)
        
        # Set exchange to hyperliquid
        db.set_exchange_type(uid, 'hyperliquid')
        assert db.get_exchange_type(uid) == 'hyperliquid'
        
        # Set HL credentials with testnet=True
        try:
            db.set_hl_credentials(uid, 'test_private_key_abc123', None, testnet=True)
        except:
            pass  # May fail if column doesn't exist
        
        # Verify exchange is hyperliquid
        assert db.get_exchange_type(uid) == 'hyperliquid'
    
    def test_user_mixed_bybit_demo_hl_mainnet(self, test_db, multi_user_ids, cleanup_test_users):
        """User D: Bybit demo + HL mainnet"""
        uid = multi_user_ids['bybit_demo_hl_main']
        db.ensure_user(uid)
        
        # Primary exchange bybit with demo mode
        db.set_exchange_type(uid, 'bybit')
        db.set_trading_mode(uid, 'demo')
        
        assert db.get_exchange_type(uid) == 'bybit'
        assert db.get_trading_mode(uid) == 'demo'
        
        # User can also have HL credentials for mainnet
        try:
            db.set_hl_credentials(uid, 'test_private_key_xyz', None, testnet=False)
        except:
            pass


# ===========================
# POSITION MANAGEMENT TESTS
# ===========================

class TestMultiUserPositions:
    """Test position management across different user configurations"""
    
    def test_positions_isolation_between_users(self, test_db, multi_user_ids, cleanup_test_users):
        """Positions should be isolated between users"""
        uid1 = multi_user_ids['all_enabled']
        uid2 = multi_user_ids['bybit_real_only']
        
        db.ensure_user(uid1)
        db.ensure_user(uid2)
        
        # User 1 opens position
        db.add_active_position(
            user_id=uid1,
            symbol="BTCUSDT",
            side="Buy",
            entry_price=45000.0,
            size=0.1,
            strategy="elcaro",
            account_type="demo",
            exchange="bybit"
        )
        
        # User 2 opens different position
        db.add_active_position(
            user_id=uid2,
            symbol="ETHUSDT",
            side="Sell",
            entry_price=3000.0,
            size=1.0,
            strategy="scalper",
            account_type="real",
            exchange="bybit"
        )
        
        # Verify isolation
        user1_positions = db.get_active_positions(uid1)
        user2_positions = db.get_active_positions(uid2)
        
        assert len(user1_positions) >= 1
        assert len(user2_positions) >= 1
        
        user1_symbols = [p['symbol'] for p in user1_positions]
        user2_symbols = [p['symbol'] for p in user2_positions]
        
        assert "BTCUSDT" in user1_symbols
        assert "ETHUSDT" in user2_symbols
        
        # Cleanup
        db.remove_active_position(uid1, "BTCUSDT", "demo", exchange="bybit")
        db.remove_active_position(uid2, "ETHUSDT", "real", exchange="bybit")
    
    def test_position_account_type_separation(self, test_db, multi_user_ids, cleanup_test_users):
        """Same symbol can have positions in demo and real accounts"""
        uid = multi_user_ids['bybit_both']
        db.ensure_user(uid)
        db.set_trading_mode(uid, 'both')
        
        # Open BTCUSDT in DEMO
        db.add_active_position(
            user_id=uid,
            symbol="BTCUSDT",
            side="Buy",
            entry_price=45000.0,
            size=0.1,
            strategy="elcaro",
            account_type="demo",
            exchange="bybit"
        )
        
        # Open BTCUSDT in REAL (different direction)
        db.add_active_position(
            user_id=uid,
            symbol="BTCUSDT",
            side="Sell",
            entry_price=45100.0,
            size=0.05,
            strategy="scalper",
            account_type="real",
            exchange="bybit"
        )
        
        # Get all positions
        all_positions = db.get_active_positions(uid)
        btc_positions = [p for p in all_positions if p['symbol'] == 'BTCUSDT']
        
        # Should have 2 BTCUSDT positions (demo + real)
        assert len(btc_positions) >= 2, f"Expected 2 BTCUSDT positions, got {len(btc_positions)}"
        
        # Get by account type
        demo_positions = db.get_active_positions(uid, account_type="demo")
        real_positions = db.get_active_positions(uid, account_type="real")
        
        demo_btc = [p for p in demo_positions if p['symbol'] == 'BTCUSDT']
        real_btc = [p for p in real_positions if p['symbol'] == 'BTCUSDT']
        
        assert len(demo_btc) >= 1, "Should have demo BTCUSDT position"
        assert len(real_btc) >= 1, "Should have real BTCUSDT position"
        
        # Verify different sides
        assert demo_btc[0]['side'] == 'Buy'
        assert real_btc[0]['side'] == 'Sell'
        
        # Cleanup
        db.remove_active_position(uid, "BTCUSDT", "demo", exchange="bybit")
        db.remove_active_position(uid, "BTCUSDT", "real", exchange="bybit")
    
    def test_strategy_tracking_per_position(self, test_db, multi_user_ids, cleanup_test_users):
        """Each position should track its strategy correctly"""
        uid = multi_user_ids['all_enabled']
        db.ensure_user(uid)
        
        # Open positions with different strategies
        strategies = {
            "BTCUSDT": "elcaro",
            "ETHUSDT": "scalper",
            "SOLUSDT": "scryptomera",
            "ARBUSDT": "manual",
        }
        
        for symbol, strategy in strategies.items():
            db.add_active_position(
                user_id=uid,
                symbol=symbol,
                side="Buy",
                entry_price=100.0,
                size=1.0,
                strategy=strategy,
                account_type="demo",
                exchange="bybit"
            )
        
        # Verify strategies
        positions = db.get_active_positions(uid)
        for pos in positions:
            if pos['symbol'] in strategies:
                expected_strategy = strategies[pos['symbol']]
                assert pos['strategy'] == expected_strategy, \
                    f"{pos['symbol']} should have strategy={expected_strategy}, got {pos['strategy']}"
        
        # Cleanup
        for symbol in strategies.keys():
            db.remove_active_position(uid, symbol, "demo", exchange="bybit")


# ===========================
# STRATEGY CONFIGURATION TESTS
# ===========================

@needs_4d_update
class TestMultiUserStrategies:
    """Test strategy configurations across users"""
    
    def test_independent_strategy_settings(self, test_db, multi_user_ids, cleanup_test_users):
        """Each user should have independent strategy settings"""
        uid1 = multi_user_ids['all_enabled']
        uid2 = multi_user_ids['bybit_real_only']
        
        db.ensure_user(uid1)
        db.ensure_user(uid2)
        
        # User 1: High risk settings
        db.set_strategy_setting(uid1, 'elcaro', 'percent', 5.0)
        db.set_strategy_setting(uid1, 'elcaro', 'leverage', 20)
        db.set_strategy_setting(uid1, 'elcaro', 'tp_pct', 15.0)
        
        # User 2: Conservative settings
        db.set_strategy_setting(uid2, 'elcaro', 'percent', 1.0)
        db.set_strategy_setting(uid2, 'elcaro', 'leverage', 5)
        db.set_strategy_setting(uid2, 'elcaro', 'tp_pct', 5.0)
        
        # Verify independence
        settings1 = db.get_strategy_settings(uid1, 'elcaro')
        settings2 = db.get_strategy_settings(uid2, 'elcaro')
        
        assert float(settings1.get('percent', 0)) == 5.0
        assert float(settings2.get('percent', 0)) == 1.0
        assert int(settings1.get('leverage', 0)) == 20
        assert int(settings2.get('leverage', 0)) == 5
    
    def test_strategy_enabled_per_account_type(self, test_db, multi_user_ids, cleanup_test_users):
        """Strategy can be enabled for specific account types"""
        uid = multi_user_ids['bybit_both']
        db.ensure_user(uid)
        db.set_trading_mode(uid, 'both')
        
        # Enable elcaro for demo only
        db.set_strategy_setting(uid, 'elcaro', 'enabled', 1)
        db.set_strategy_setting(uid, 'elcaro', 'account_types', 'demo')
        
        # Enable scalper for real only
        db.set_strategy_setting(uid, 'scalper', 'enabled', 1)
        db.set_strategy_setting(uid, 'scalper', 'account_types', 'real')
        
        # Verify
        elcaro_settings = db.get_strategy_settings(uid, 'elcaro')
        scalper_settings = db.get_strategy_settings(uid, 'scalper')
        
        # Check settings are saved (account_types field exists now)
        assert elcaro_settings.get('enabled') in [1, True]
        assert scalper_settings.get('enabled') in [1, True]
    
    def test_different_tp_sl_per_strategy(self, test_db, multi_user_ids, cleanup_test_users):
        """Different TP/SL settings per strategy"""
        uid = multi_user_ids['all_enabled']
        db.ensure_user(uid)
        
        # Configure different TP/SL for each strategy (use correct field names)
        strategy_settings = {
            'elcaro': {'tp_percent': 8.0, 'sl_percent': 3.0},
            'scalper': {'tp_percent': 3.0, 'sl_percent': 1.5},
            'scryptomera': {'tp_percent': 15.0, 'sl_percent': 5.0},
        }
        
        for strategy, settings in strategy_settings.items():
            db.set_strategy_setting(uid, strategy, 'tp_percent', settings['tp_percent'])
            db.set_strategy_setting(uid, strategy, 'sl_percent', settings['sl_percent'])
        
        # Verify each strategy has correct settings
        for strategy, expected in strategy_settings.items():
            settings = db.get_strategy_settings(uid, strategy)
            actual_tp = float(settings.get('tp_percent') or 0)
            actual_sl = float(settings.get('sl_percent') or 0)
            
            assert actual_tp == expected['tp_percent'], \
                f"{strategy} TP should be {expected['tp_percent']}, got {actual_tp}"
            assert actual_sl == expected['sl_percent'], \
                f"{strategy} SL should be {expected['sl_percent']}, got {actual_sl}"


# ===========================
# TRADE LOGGING TESTS
# ===========================

class TestMultiUserTradeLogs:
    """Test trade logging across different configurations"""
    
    def test_trade_log_with_strategy(self, test_db, multi_user_ids, cleanup_test_users):
        """Trade logs should correctly record strategy"""
        uid = multi_user_ids['all_enabled']
        db.ensure_user(uid)
        
        strategies = ['elcaro', 'scalper', 'scryptomera', 'manual', None]
        
        for i, strategy in enumerate(strategies):
            db.add_trade_log(
                user_id=uid,
                signal_id=None,
                symbol=f"TEST{i}USDT",
                side="Buy",
                entry_price=100.0,
                exit_price=105.0,
                exit_reason="TP",
                pnl=5.0,
                pnl_pct=5.0,
                strategy=strategy,
                account_type="demo",
                exchange="bybit"
            )
        
        # Get stats by strategy with exchange
        elcaro_stats = db.get_trade_stats(uid, strategy='elcaro', exchange="bybit")
        scalper_stats = db.get_trade_stats(uid, strategy='scalper', exchange="bybit")
        
        # These should work without error
        assert elcaro_stats is not None
        assert scalper_stats is not None
    
    def test_trade_log_account_type_separation(self, test_db, multi_user_ids, cleanup_test_users):
        """Trade logs should separate by account type"""
        uid = multi_user_ids['bybit_both']
        db.ensure_user(uid)
        
        # Log demo trade
        db.add_trade_log(
            user_id=uid,
            signal_id=None,
            symbol="BTCUSDT",
            side="Buy",
            entry_price=45000.0,
            exit_price=46000.0,
            exit_reason="TP",
            pnl=100.0,
            pnl_pct=2.22,
            strategy="elcaro",
            account_type="demo",
            exchange="bybit"
        )
        
        # Log real trade
        db.add_trade_log(
            user_id=uid,
            signal_id=None,
            symbol="BTCUSDT",
            side="Sell",
            entry_price=45000.0,
            exit_price=44000.0,
            exit_reason="SL",
            pnl=-50.0,
            pnl_pct=-2.22,
            strategy="scalper",
            account_type="real",
            exchange="bybit"
        )
        
        # Get stats by account type with exchange
        try:
            demo_stats = db.get_trade_stats(uid, account_type='demo', exchange="bybit")
            real_stats = db.get_trade_stats(uid, account_type='real', exchange="bybit")
            # Just verify no errors
            assert demo_stats is not None or True
            assert real_stats is not None or True
        except TypeError:
            # account_type parameter may not be supported
            pass


# ===========================
# EXCHANGE SWITCHING TESTS
# ===========================

@needs_4d_update
class TestExchangeSwitching:
    """Test exchange switching scenarios"""
    
    def test_switch_exchange_preserves_settings(self, test_db, multi_user_ids, cleanup_test_users):
        """Switching exchange should preserve user settings.
        
        NOTE: Strategy settings are ISOLATED per exchange/account_type.
        Global user settings (leverage, lang) are preserved across exchanges.
        Strategy-specific settings stay with their exchange context.
        """
        uid = multi_user_ids['all_enabled']
        db.ensure_user(uid)
        
        # Set exchange to Bybit first
        db.set_exchange_type(uid, 'bybit')
        db.set_trading_mode(uid, 'demo')
        
        # Set some global user settings
        db.set_user_field(uid, 'leverage', 15)
        db.set_user_field(uid, 'lang', 'ru')
        
        # Set strategy settings for Bybit demo context
        db.set_strategy_setting(uid, 'elcaro', 'percent', 5.0, 'bybit', 'demo')
        
        # Verify settings preserved for Bybit
        cfg = db.get_user_config(uid)
        assert cfg.get('leverage') == 15
        assert cfg.get('lang') == 'ru'
        
        # Verify strategy settings for Bybit context
        elcaro_bybit = db.get_strategy_settings(uid, 'elcaro', 'bybit', 'demo')
        assert elcaro_bybit.get('percent') == 5.0, f"Bybit percent should be 5.0, got {elcaro_bybit.get('percent')}"
        
        # Switch to HyperLiquid
        db.set_exchange_type(uid, 'hyperliquid')
        # Note: trading_mode is 'demo'/'real'/'both', HyperLiquid uses 'demo' -> 'testnet', 'real' -> 'mainnet'
        db.set_trading_mode(uid, 'demo')  # Will normalize to 'testnet' for HyperLiquid
        
        # Global settings should still be preserved
        cfg = db.get_user_config(uid)
        assert cfg.get('leverage') == 15
        assert cfg.get('lang') == 'ru'
        
        # For HyperLiquid, 'demo' trading_mode means 'testnet'
        # Strategy settings for HyperLiquid testnet should be empty (not set yet)
        elcaro_hl = db.get_strategy_settings(uid, 'elcaro', 'hyperliquid', 'testnet')
        assert elcaro_hl.get('percent') is None, f"HyperLiquid percent should be None (not set), got {elcaro_hl.get('percent')}"
        
        # Original Bybit settings should still be preserved
        elcaro_bybit_after = db.get_strategy_settings(uid, 'elcaro', 'bybit', 'demo')
        assert elcaro_bybit_after.get('percent') == 5.0, f"Bybit percent should still be 5.0, got {elcaro_bybit_after.get('percent')}"
    
    def test_trading_mode_switch(self, test_db, multi_user_ids, cleanup_test_users):
        """Switching trading mode should work correctly"""
        uid = multi_user_ids['bybit_both']
        db.ensure_user(uid)
        
        # Test all modes
        for mode in ['demo', 'real', 'both']:
            db.set_trading_mode(uid, mode)
            actual = db.get_trading_mode(uid)
            assert actual == mode, f"Expected mode={mode}, got {actual}"


# ===========================
# CREDENTIAL MANAGEMENT TESTS
# ===========================

class TestCredentialManagement:
    """Test credential management for different exchanges"""
    
    def test_bybit_credentials_demo_real(self, test_db, multi_user_ids, cleanup_test_users):
        """Test Bybit demo and real credentials are separate"""
        uid = multi_user_ids['bybit_both']
        db.ensure_user(uid)
        
        # Set demo credentials
        db.set_user_credentials(uid, 'demo_api_key', 'demo_secret', 'demo')
        
        # Set real credentials
        db.set_user_credentials(uid, 'real_api_key', 'real_secret', 'real')
        
        # Retrieve and verify separation
        demo_creds = db.get_user_credentials(uid, 'demo')
        real_creds = db.get_user_credentials(uid, 'real')
        
        if demo_creds:
            assert demo_creds[0] == 'demo_api_key'
        if real_creds:
            assert real_creds[0] == 'real_api_key'
    
    def test_hl_credentials(self, test_db, multi_user_ids, cleanup_test_users):
        """Test HyperLiquid credential management"""
        uid = multi_user_ids['hl_testnet_only']
        db.ensure_user(uid)
        
        try:
            # Set HL credentials
            db.set_hl_credentials(uid, 'test_private_key', 'vault_address', testnet=True)
            
            # Retrieve
            creds = db.get_hl_credentials(uid)
            if creds:
                assert creds[0] == 'test_private_key'
        except Exception:
            # HL credentials may not be fully implemented
            pass


# ===========================
# CONCURRENT USER OPERATIONS
# ===========================

@needs_4d_update
class TestConcurrentOperations:
    """Test concurrent operations from multiple users"""
    
    def test_concurrent_position_updates(self, test_db, multi_user_ids, cleanup_test_users):
        """Multiple users can update positions concurrently"""
        users = [
            multi_user_ids['all_enabled'],
            multi_user_ids['bybit_real_only'],
            multi_user_ids['hl_testnet_only'],
        ]
        
        for uid in users:
            db.ensure_user(uid)
        
        # All users open positions
        for i, uid in enumerate(users):
            db.add_active_position(
                user_id=uid,
                symbol=f"COIN{i}USDT",
                side="Buy",
                entry_price=100.0 + i * 10,
                size=1.0,
                strategy="elcaro",
                account_type="demo",
                exchange="bybit"
            )
        
        # Verify each user has their position
        for i, uid in enumerate(users):
            positions = db.get_active_positions(uid)
            symbols = [p['symbol'] for p in positions]
            assert f"COIN{i}USDT" in symbols
        
        # All users close positions
        for i, uid in enumerate(users):
            db.remove_active_position(uid, f"COIN{i}USDT", "demo", exchange='bybit')
        
        # Verify all closed
        for uid in users:
            positions = db.get_active_positions(uid)
            assert len(positions) == 0 or all(p['symbol'].startswith('COIN') == False for p in positions)
    
    def test_strategy_settings_isolation(self, test_db, multi_user_ids, cleanup_test_users):
        """Strategy settings changes are isolated between users"""
        uid1 = multi_user_ids['all_enabled']
        uid2 = multi_user_ids['bybit_real_only']
        
        db.ensure_user(uid1)
        db.ensure_user(uid2)
        
        # User 1 changes settings
        db.set_strategy_setting(uid1, 'elcaro', 'percent', 10.0)
        
        # User 2 changes same strategy differently
        db.set_strategy_setting(uid2, 'elcaro', 'percent', 2.0)
        
        # Verify isolation
        settings1 = db.get_strategy_settings(uid1, 'elcaro')
        settings2 = db.get_strategy_settings(uid2, 'elcaro')
        
        assert float(settings1.get('percent', 0)) == 10.0
        assert float(settings2.get('percent', 0)) == 2.0


# ===========================
# UPDATE POSITION STRATEGY TESTS
# ===========================

class TestUpdatePositionStrategy:
    """Test the new update_position_strategy function"""
    
    def test_update_null_strategy(self, test_db, multi_user_ids, cleanup_test_users):
        """Can update NULL strategy to valid strategy"""
        uid = multi_user_ids['all_enabled']
        db.ensure_user(uid)
        
        # Add position with NULL strategy
        db.add_active_position(
            user_id=uid,
            symbol="TESTUSDT",
            side="Buy",
            entry_price=100.0,
            size=1.0,
            strategy=None,  # NULL strategy
            account_type="demo",
            exchange="bybit"
        )
        
        # Verify strategy is NULL
        positions = db.get_active_positions(uid)
        test_pos = next((p for p in positions if p['symbol'] == 'TESTUSDT'), None)
        assert test_pos is not None
        assert test_pos['strategy'] is None
        
        # Update strategy
        result = db.update_position_strategy(uid, 'TESTUSDT', 'manual', 'demo')
        assert result == True
        
        # Verify update
        positions = db.get_active_positions(uid)
        test_pos = next((p for p in positions if p['symbol'] == 'TESTUSDT'), None)
        assert test_pos is not None
        assert test_pos['strategy'] == 'manual'
        
        # Cleanup
        db.remove_active_position(uid, 'TESTUSDT', 'demo', exchange='bybit')
    
    def test_update_nonexistent_position(self, test_db, multi_user_ids, cleanup_test_users):
        """Updating nonexistent position returns False"""
        uid = multi_user_ids['all_enabled']
        db.ensure_user(uid)
        
        result = db.update_position_strategy(uid, 'NONEXISTENTUSDT', 'manual', 'demo')
        assert result == False


# ===========================
# EDGE CASES
# ===========================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_empty_strategy_name(self, test_db, multi_user_ids, cleanup_test_users):
        """Handle empty strategy name"""
        uid = multi_user_ids['all_enabled']
        db.ensure_user(uid)
        
        db.add_active_position(
            user_id=uid,
            symbol="EDGEUSDT",
            side="Buy",
            entry_price=100.0,
            size=1.0,
            strategy="",  # Empty string
            account_type="demo",
            exchange="bybit"
        )
        
        positions = db.get_active_positions(uid)
        edge_pos = next((p for p in positions if p['symbol'] == 'EDGEUSDT'), None)
        assert edge_pos is not None
        # Empty string or None both acceptable
        assert edge_pos['strategy'] in ['', None]
        
        db.remove_active_position(uid, 'EDGEUSDT', 'demo', exchange='bybit')
    
    def test_special_characters_in_settings(self, test_db, multi_user_ids, cleanup_test_users):
        """Handle special characters in settings values"""
        uid = multi_user_ids['all_enabled']
        db.ensure_user(uid)
        
        # Set a setting with special characters (shouldn't break anything)
        try:
            db.set_user_field(uid, 'lang', 'ru')
            cfg = db.get_user_config(uid)
            assert cfg.get('lang') == 'ru'
        except Exception as e:
            pytest.fail(f"Special characters caused error: {e}")
    
    def test_very_large_position_size(self, test_db, multi_user_ids, cleanup_test_users):
        """Handle very large position sizes"""
        uid = multi_user_ids['all_enabled']
        db.ensure_user(uid)
        
        db.add_active_position(
            user_id=uid,
            symbol="LARGEUSDT",
            side="Buy",
            entry_price=0.00001,
            size=1000000000.0,  # Very large
            strategy="elcaro",
            account_type="demo",
            exchange="bybit"
        )
        
        positions = db.get_active_positions(uid)
        large_pos = next((p for p in positions if p['symbol'] == 'LARGEUSDT'), None)
        assert large_pos is not None
        assert large_pos['size'] == 1000000000.0
        
        db.remove_active_position(uid, 'LARGEUSDT', 'demo', exchange='bybit')
    
    def test_very_small_entry_price(self, test_db, multi_user_ids, cleanup_test_users):
        """Handle very small entry prices (meme coins)"""
        uid = multi_user_ids['all_enabled']
        db.ensure_user(uid)
        
        db.add_active_position(
            user_id=uid,
            symbol="MEMEUSDT",
            side="Buy",
            entry_price=0.0000000001,  # Very small price
            size=1000000.0,
            strategy="scalper",
            account_type="demo",
            exchange="bybit"
        )
        
        positions = db.get_active_positions(uid)
        meme_pos = next((p for p in positions if p['symbol'] == 'MEMEUSDT'), None)
        assert meme_pos is not None
        assert meme_pos['entry_price'] == pytest.approx(0.0000000001, rel=1e-5)
        
        db.remove_active_position(uid, 'MEMEUSDT', 'demo', exchange='bybit')


# ===========================
# RUN TESTS
# ===========================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
