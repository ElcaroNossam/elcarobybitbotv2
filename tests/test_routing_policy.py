"""
Tests for Routing Policy and Execution Targets system.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import db
from db import (
    RoutingPolicy,
    get_routing_policy,
    set_routing_policy,
    get_live_enabled,
    set_live_enabled,
    get_execution_targets,
    get_strategy_settings,
    init_db,
    ensure_user,
)


# Test user ID
TEST_USER_ID = 999999999


@pytest.fixture(autouse=True)
def setup_db():
    """Initialize DB before each test."""
    init_db()
    ensure_user(TEST_USER_ID)
    # Reset to defaults
    with db.get_conn() as conn:
        conn.execute("""
            UPDATE users SET 
                routing_policy = 'same_exchange_all_envs',
                live_enabled = 0,
                trading_mode = 'demo',
                exchange_type = 'bybit',
                demo_api_key = 'test_key',
                demo_api_secret = 'test_secret'
            WHERE user_id = ?
        """, (TEST_USER_ID,))
        conn.commit()
    db.invalidate_user_cache(TEST_USER_ID)
    yield
    # Cleanup
    with db.get_conn() as conn:
        conn.execute("DELETE FROM users WHERE user_id = ?", (TEST_USER_ID,))
        conn.execute("DELETE FROM user_strategy_settings WHERE user_id = ?", (TEST_USER_ID,))
        conn.commit()


class TestRoutingPolicy:
    """Test routing policy CRUD operations."""
    
    def test_default_routing_policy(self):
        """Default should be SAME_EXCHANGE_ALL_ENVS."""
        policy = get_routing_policy(TEST_USER_ID)
        assert policy == RoutingPolicy.SAME_EXCHANGE_ALL_ENVS
    
    def test_set_routing_policy_active_only(self):
        """Can set to ACTIVE_ONLY."""
        set_routing_policy(TEST_USER_ID, RoutingPolicy.ACTIVE_ONLY)
        assert get_routing_policy(TEST_USER_ID) == RoutingPolicy.ACTIVE_ONLY
    
    def test_set_routing_policy_all_enabled(self):
        """Can set to ALL_ENABLED."""
        set_routing_policy(TEST_USER_ID, RoutingPolicy.ALL_ENABLED)
        assert get_routing_policy(TEST_USER_ID) == RoutingPolicy.ALL_ENABLED
    
    def test_invalid_routing_policy_raises(self):
        """Invalid policy should raise ValueError."""
        with pytest.raises(ValueError):
            set_routing_policy(TEST_USER_ID, "invalid_policy")


class TestLiveEnabled:
    """Test live_enabled safety flag."""
    
    def test_default_live_disabled(self):
        """Default should be disabled."""
        assert get_live_enabled(TEST_USER_ID) == False
    
    def test_enable_live(self):
        """Can enable live trading."""
        set_live_enabled(TEST_USER_ID, True)
        assert get_live_enabled(TEST_USER_ID) == True
    
    def test_disable_live(self):
        """Can disable live trading."""
        set_live_enabled(TEST_USER_ID, True)
        set_live_enabled(TEST_USER_ID, False)
        assert get_live_enabled(TEST_USER_ID) == False


class TestGetExecutionTargets:
    """Test get_execution_targets function."""
    
    def test_active_only_policy_paper(self):
        """ACTIVE_ONLY returns only current target."""
        set_routing_policy(TEST_USER_ID, RoutingPolicy.ACTIVE_ONLY)
        targets = get_execution_targets(TEST_USER_ID)
        
        assert len(targets) == 1
        assert targets[0]["exchange"] == "bybit"
        assert targets[0]["env"] == "paper"
        assert targets[0]["account_type"] == "demo"
    
    def test_active_only_policy_live_blocked(self):
        """ACTIVE_ONLY with live target but live_enabled=False returns empty."""
        # Set trading mode to real
        with db.get_conn() as conn:
            conn.execute("""
                UPDATE users SET 
                    trading_mode = 'real',
                    real_api_key = 'real_key',
                    real_api_secret = 'real_secret'
                WHERE user_id = ?
            """, (TEST_USER_ID,))
            conn.commit()
        db.invalidate_user_cache(TEST_USER_ID)
        
        set_routing_policy(TEST_USER_ID, RoutingPolicy.ACTIVE_ONLY)
        targets = get_execution_targets(TEST_USER_ID)
        
        # Live not enabled, should be empty
        assert len(targets) == 0
    
    def test_active_only_policy_live_enabled(self):
        """ACTIVE_ONLY with live target and live_enabled=True works."""
        # Set trading mode to real
        with db.get_conn() as conn:
            conn.execute("""
                UPDATE users SET 
                    trading_mode = 'real',
                    real_api_key = 'real_key',
                    real_api_secret = 'real_secret'
                WHERE user_id = ?
            """, (TEST_USER_ID,))
            conn.commit()
        db.invalidate_user_cache(TEST_USER_ID)
        
        set_routing_policy(TEST_USER_ID, RoutingPolicy.ACTIVE_ONLY)
        set_live_enabled(TEST_USER_ID, True)
        
        targets = get_execution_targets(TEST_USER_ID)
        
        assert len(targets) == 1
        assert targets[0]["env"] == "live"
        assert targets[0]["account_type"] == "real"
    
    def test_same_exchange_all_envs_demo_only(self):
        """SAME_EXCHANGE_ALL_ENVS with only demo configured."""
        targets = get_execution_targets(TEST_USER_ID)
        
        # Only demo configured, live_enabled=False
        assert len(targets) == 1
        assert targets[0]["env"] == "paper"
    
    def test_same_exchange_all_envs_both_modes(self):
        """SAME_EXCHANGE_ALL_ENVS with both demo and real."""
        # Setup both
        with db.get_conn() as conn:
            conn.execute("""
                UPDATE users SET 
                    trading_mode = 'both',
                    demo_api_key = 'demo_key',
                    demo_api_secret = 'demo_secret',
                    real_api_key = 'real_key',
                    real_api_secret = 'real_secret'
                WHERE user_id = ?
            """, (TEST_USER_ID,))
            conn.commit()
        db.invalidate_user_cache(TEST_USER_ID)
        
        set_live_enabled(TEST_USER_ID, True)
        
        targets = get_execution_targets(TEST_USER_ID)
        
        # Should have both paper and live
        assert len(targets) == 2
        envs = {t["env"] for t in targets}
        assert "paper" in envs
        assert "live" in envs
    
    def test_live_filtered_when_not_enabled(self):
        """Live targets are filtered when live_enabled=False."""
        # Setup both
        with db.get_conn() as conn:
            conn.execute("""
                UPDATE users SET 
                    trading_mode = 'both',
                    demo_api_key = 'demo_key',
                    demo_api_secret = 'demo_secret',
                    real_api_key = 'real_key',
                    real_api_secret = 'real_secret'
                WHERE user_id = ?
            """, (TEST_USER_ID,))
            conn.commit()
        db.invalidate_user_cache(TEST_USER_ID)
        
        # live_enabled = False (default)
        targets = get_execution_targets(TEST_USER_ID)
        
        # Should only have paper
        assert len(targets) == 1
        assert targets[0]["env"] == "paper"


class TestStrategySettingsFallback:
    """Test strategy settings fallback logic."""
    
    def test_fallback_to_defaults(self):
        """When no custom settings, returns defaults."""
        settings = get_strategy_settings(TEST_USER_ID, "elcaro", "bybit", "demo")
        
        # Should have default structure
        assert "percent" in settings
        assert "sl_percent" in settings
        assert "tp_percent" in settings
    
    def test_custom_settings_override(self):
        """Custom settings override defaults."""
        # Insert custom settings
        with db.get_conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO user_strategy_settings 
                (user_id, strategy, exchange, account_type, percent, sl_percent, tp_percent)
                VALUES (?, 'elcaro', 'bybit', 'demo', 2.5, 5.0, 15.0)
            """, (TEST_USER_ID,))
            conn.commit()
        
        settings = get_strategy_settings(TEST_USER_ID, "elcaro", "bybit", "demo")
        
        assert settings["percent"] == 2.5
        assert settings["sl_percent"] == 5.0
        assert settings["tp_percent"] == 15.0


class TestRoutingPolicyEnums:
    """Test RoutingPolicy enum values."""
    
    def test_active_only_value(self):
        assert RoutingPolicy.ACTIVE_ONLY == "active_only"
    
    def test_same_exchange_value(self):
        assert RoutingPolicy.SAME_EXCHANGE_ALL_ENVS == "same_exchange_all_envs"
    
    def test_all_enabled_value(self):
        assert RoutingPolicy.ALL_ENABLED == "all_enabled"
    
    def test_custom_value(self):
        assert RoutingPolicy.CUSTOM == "custom"
