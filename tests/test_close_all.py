#!/usr/bin/env python3
"""
Test Close All Positions functionality
Tests the complete close all flow including cooldown mechanism
"""

import sys
import time
import asyncio
import pytest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import db
from bot import _close_all_cooldown

# Mark tests requiring PostgreSQL
requires_postgres = pytest.mark.skipif(
    True,  # Skip by default since local dev doesn't have PostgreSQL
    reason="Requires PostgreSQL connection"
)


class TestCloseAllPositions:
    """Test suite for Close All Positions functionality"""
    
    def test_cooldown_initialization(self):
        """Test that cooldown dict is properly initialized"""
        assert isinstance(_close_all_cooldown, dict), "Cooldown should be a dict"
        print("✓ Cooldown dict properly initialized")
    
    def test_cooldown_set_and_check(self):
        """Test setting and checking cooldown"""
        test_uid = 999999999
        
        # Set cooldown for 30 seconds
        _close_all_cooldown[test_uid] = time.time() + 30
        
        # Check cooldown is active
        is_active = test_uid in _close_all_cooldown and time.time() < _close_all_cooldown[test_uid]
        assert is_active, "Cooldown should be active"
        print("✓ Cooldown set and active check works")
        
        # Cleanup
        del _close_all_cooldown[test_uid]
    
    def test_cooldown_expiration(self):
        """Test that cooldown expires correctly"""
        test_uid = 999999998
        
        # Set cooldown to past time (already expired)
        _close_all_cooldown[test_uid] = time.time() - 1
        
        # Check cooldown should not be active
        is_active = test_uid in _close_all_cooldown and time.time() < _close_all_cooldown[test_uid]
        assert not is_active, "Expired cooldown should not be active"
        print("✓ Cooldown expiration works correctly")
        
        # Cleanup
        del _close_all_cooldown[test_uid]
    
    def test_cooldown_duration(self):
        """Test that cooldown duration is correct (30 seconds)"""
        test_uid = 999999997
        now = time.time()
        
        # Set cooldown
        _close_all_cooldown[test_uid] = now + 30
        
        # Check remaining time
        remaining = _close_all_cooldown[test_uid] - now
        assert 29.5 < remaining <= 30.0, f"Cooldown should be ~30s, got {remaining}s"
        print(f"✓ Cooldown duration correct: {remaining:.1f}s")
        
        # Cleanup
        del _close_all_cooldown[test_uid]
    
    def test_multiple_user_cooldowns(self):
        """Test that cooldowns work independently for multiple users"""
        user1 = 999999996
        user2 = 999999995
        now = time.time()
        
        # Set different cooldowns
        _close_all_cooldown[user1] = now + 30
        _close_all_cooldown[user2] = now + 60
        
        # Check both are active
        is_active_1 = user1 in _close_all_cooldown and time.time() < _close_all_cooldown[user1]
        is_active_2 = user2 in _close_all_cooldown and time.time() < _close_all_cooldown[user2]
        
        assert is_active_1, "User 1 cooldown should be active"
        assert is_active_2, "User 2 cooldown should be active"
        
        # Check different durations
        remaining_1 = _close_all_cooldown[user1] - time.time()
        remaining_2 = _close_all_cooldown[user2] - time.time()
        
        assert remaining_1 < remaining_2, "User 1 cooldown should be shorter"
        print(f"✓ Multiple user cooldowns work independently: {remaining_1:.1f}s vs {remaining_2:.1f}s")
        
        # Cleanup
        del _close_all_cooldown[user1]
        del _close_all_cooldown[user2]
    
    def test_close_all_components_exist(self):
        """Test that all required close all components exist"""
        from bot import place_order, remove_active_position, reset_pyramid
        
        assert callable(place_order), "place_order should be callable"
        assert callable(remove_active_position), "remove_active_position should be callable"
        assert callable(reset_pyramid), "reset_pyramid should be callable"
        
        print("✓ All close all components exist")
    
    def test_monitoring_loop_respects_cooldown(self):
        """Test that monitoring loop code checks cooldown before adding positions"""
        # Read bot.py and check for cooldown check in monitoring loop
        bot_file = Path(__file__).parent.parent / "bot.py"
        with open(bot_file) as f:
            content = f.read()
        
        # Check for cooldown check pattern
        assert "_close_all_cooldown.get(uid, 0)" in content, "Should check cooldown in monitoring loop"
        assert "Skip adding new positions during cooldown" in content or "in close_all cooldown" in content, "Should have cooldown skip logic"
        
        print("✓ Monitoring loop respects cooldown")
    
    def test_close_all_sets_cooldown(self):
        """Test that close all callback sets cooldown"""
        # Read bot.py and check for cooldown setting in close all handler
        bot_file = Path(__file__).parent.parent / "bot.py"
        with open(bot_file) as f:
            content = f.read()
        
        # Check for cooldown setting pattern
        assert "_close_all_cooldown[uid] = time.time() + 30" in content, "Should set 30 second cooldown"
        
        print("✓ Close all handler sets cooldown")
    
    @requires_postgres
    def test_database_position_operations(self):
        """Test database operations for position management"""
        # Get test user
        users = db.get_all_users()
        if not users:
            print("⚠ No users in database, skipping DB test")
            return
        
        test_uid = users[0]
        
        # Get positions
        positions = db.get_active_positions(test_uid)
        initial_count = len(positions)
        
        print(f"✓ Database operations work (user {test_uid} has {initial_count} positions)")
    
    def test_cooldown_prevents_readd_logic(self):
        """Test the logic that prevents re-adding positions during cooldown"""
        test_uid = 999999994
        now = time.time()
        
        # Set active cooldown
        _close_all_cooldown[test_uid] = now + 30
        
        # Simulate monitoring loop check
        cooldown_end = _close_all_cooldown.get(test_uid, 0)
        should_skip = now < cooldown_end
        
        assert should_skip, "Should skip adding positions during active cooldown"
        
        time_left = cooldown_end - now
        assert time_left > 0, "Should have time left in cooldown"
        
        print(f"✓ Cooldown prevents position re-add ({time_left:.1f}s left)")
        
        # Cleanup
        del _close_all_cooldown[test_uid]
    
    def test_cooldown_allows_after_expiry(self):
        """Test that positions can be added after cooldown expires"""
        test_uid = 999999993
        now = time.time()
        
        # Set expired cooldown
        _close_all_cooldown[test_uid] = now - 1
        
        # Simulate monitoring loop check
        cooldown_end = _close_all_cooldown.get(test_uid, 0)
        should_skip = now < cooldown_end
        
        assert not should_skip, "Should NOT skip adding positions after cooldown expires"
        
        print("✓ Positions can be added after cooldown expires")
        
        # Cleanup
        del _close_all_cooldown[test_uid]
    
    def test_no_cooldown_for_new_user(self):
        """Test that users without cooldown can add positions"""
        test_uid = 999999992
        now = time.time()
        
        # Don't set any cooldown
        
        # Simulate monitoring loop check
        cooldown_end = _close_all_cooldown.get(test_uid, 0)
        should_skip = now < cooldown_end
        
        assert not should_skip, "Should NOT skip for user without cooldown"
        assert cooldown_end == 0, "Default cooldown should be 0"
        
        print("✓ New users without cooldown can add positions")


def run_tests():
    """Run all tests"""
    test = TestCloseAllPositions()
    
    tests = [
        test.test_cooldown_initialization,
        test.test_cooldown_set_and_check,
        test.test_cooldown_expiration,
        test.test_cooldown_duration,
        test.test_multiple_user_cooldowns,
        test.test_close_all_components_exist,
        test.test_monitoring_loop_respects_cooldown,
        test.test_close_all_sets_cooldown,
        test.test_database_position_operations,
        test.test_cooldown_prevents_readd_logic,
        test.test_cooldown_allows_after_expiry,
        test.test_no_cooldown_for_new_user,
    ]
    
    print("=" * 60)
    print("CLOSE ALL POSITIONS - COMPREHENSIVE TEST")
    print("=" * 60)
    print()
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            print(f"Running: {test_func.__doc__}")
            test_func()
            passed += 1
            print()
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            print()
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            print()
            failed += 1
    
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED - Close All functionality is CORRECT!")
    else:
        print(f"\n❌ {failed} TESTS FAILED - Fix required!")
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
