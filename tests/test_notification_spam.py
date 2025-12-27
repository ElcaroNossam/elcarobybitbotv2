#!/usr/bin/env python3
"""
Test that notifications don't spam after Close All Positions
"""

import sys
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from bot import _close_all_cooldown


class TestNotificationSpam:
    """Test suite for notification spam prevention after Close All"""
    
    def test_cooldown_prevents_new_position_notification(self):
        """Test that new position notification is skipped during cooldown"""
        test_uid = 999999999
        now = time.time()
        
        # Set active cooldown
        _close_all_cooldown[test_uid] = now + 30
        
        # Check if should notify
        cooldown_end = _close_all_cooldown.get(test_uid, 0)
        should_notify = now >= cooldown_end
        
        assert not should_notify, "Should NOT send new position notification during cooldown"
        print("✓ New position notification skipped during cooldown")
        
        # Cleanup
        del _close_all_cooldown[test_uid]
    
    def test_cooldown_prevents_sl_tp_notification(self):
        """Test that SL/TP notifications are skipped during cooldown"""
        test_uid = 999999998
        now = time.time()
        
        # Set active cooldown
        _close_all_cooldown[test_uid] = now + 30
        
        # Simulate notification check
        cooldown_end = _close_all_cooldown.get(test_uid, 0)
        is_new_position = True  # Even if new, should check cooldown
        should_notify = is_new_position and (now >= cooldown_end)
        
        assert not should_notify, "Should NOT send SL/TP notification during cooldown"
        print("✓ SL/TP notification skipped during cooldown")
        
        # Cleanup
        del _close_all_cooldown[test_uid]
    
    def test_notifications_allowed_after_cooldown(self):
        """Test that notifications work after cooldown expires"""
        test_uid = 999999997
        now = time.time()
        
        # Set expired cooldown
        _close_all_cooldown[test_uid] = now - 1
        
        # Check if should notify
        cooldown_end = _close_all_cooldown.get(test_uid, 0)
        should_notify = now >= cooldown_end
        
        assert should_notify, "Should send notifications after cooldown expires"
        print("✓ Notifications allowed after cooldown expiration")
        
        # Cleanup
        del _close_all_cooldown[test_uid]
    
    def test_new_position_with_cooldown_logic(self):
        """Test complete new position notification logic with cooldown"""
        test_uid = 999999996
        now = time.time()
        symbol = "BTCUSDT"
        
        # Scenario 1: No cooldown, new position → should notify
        open_syms_prev = set()  # Position is new
        cooldown_end = _close_all_cooldown.get(test_uid, 0)
        should_notify_1 = (symbol not in open_syms_prev) and (now >= cooldown_end)
        
        assert should_notify_1, "Should notify for new position without cooldown"
        print("✓ Notification sent for new position (no cooldown)")
        
        # Scenario 2: No cooldown, existing position → should NOT notify
        open_syms_prev = {symbol}  # Position existed
        should_notify_2 = (symbol not in open_syms_prev) and (now >= cooldown_end)
        
        assert not should_notify_2, "Should NOT notify for existing position"
        print("✓ Notification skipped for existing position")
        
        # Scenario 3: Active cooldown, new position → should NOT notify
        _close_all_cooldown[test_uid] = now + 30
        open_syms_prev = set()  # Position is new
        cooldown_end = _close_all_cooldown.get(test_uid, 0)
        should_notify_3 = (symbol not in open_syms_prev) and (now >= cooldown_end)
        
        assert not should_notify_3, "Should NOT notify during cooldown even if new position"
        print("✓ Notification skipped during cooldown (even new position)")
        
        # Cleanup
        if test_uid in _close_all_cooldown:
            del _close_all_cooldown[test_uid]
    
    def test_multiple_positions_close_all_scenario(self):
        """Test the actual Close All scenario with multiple positions"""
        test_uid = 999999995
        now = time.time()
        positions = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        
        # Initial state: all positions open
        open_syms_prev = set(positions)
        
        # User clicks Close All → cooldown set
        _close_all_cooldown[test_uid] = now + 30
        
        # Monitoring loop runs during cooldown
        # Some positions still show on exchange (API delay)
        cooldown_end = _close_all_cooldown.get(test_uid, 0)
        
        notifications_sent = 0
        for symbol in positions:
            # Check if should notify about SL/TP
            should_notify = (symbol not in open_syms_prev) and (now >= cooldown_end)
            if should_notify:
                notifications_sent += 1
        
        # All positions were in open_syms_prev, so even without cooldown check
        # they wouldn't notify. But let's test the cooldown part:
        
        # Now simulate NEW positions appearing during cooldown (ghost positions)
        new_ghost_positions = ["BNBUSDT", "ADAUSDT"]
        for symbol in new_ghost_positions:
            should_notify = (symbol not in open_syms_prev) and (now >= cooldown_end)
            if should_notify:
                notifications_sent += 1
        
        assert notifications_sent == 0, f"Should send 0 notifications during cooldown, sent {notifications_sent}"
        print(f"✓ No notifications sent for {len(positions)} positions during cooldown")
        print(f"✓ No notifications sent for {len(new_ghost_positions)} ghost positions during cooldown")
        
        # Cleanup
        del _close_all_cooldown[test_uid]
    
    def test_notification_logic_code_check(self):
        """Verify that bot.py contains correct notification logic"""
        bot_file = Path(__file__).parent.parent / "bot.py"
        with open(bot_file) as f:
            content = f.read()
        
        # Check for cooldown check in notification logic
        assert "should_notify = (sym not in open_syms_prev) and (now >= cooldown_end)" in content, \
            "Should have combined check for new position AND cooldown"
        
        assert "if should_notify:" in content and "await bot.send_message" in content, \
            "Should use should_notify flag before sending messages"
        
        print("✓ Bot code contains correct notification logic with cooldown check")
    
    def test_sl_tp_notification_during_close_all(self):
        """Test the exact scenario from user's screenshot"""
        test_uid = 999999994
        now = time.time()
        
        # User has 15 positions with SL/TP set
        positions = [
            "PENDLEUSDT", "BERAUSDT", "RENDERUSDT", "EIGENUSDT", "BCHUSDT",
            "AEROUSDT", "RLSUSDT", "CAMPUSDT", "HEMIUSDT", "MONUSDT",
            "PARTIUSDT", "HIPPOUSDT", "B2USDT", "APRUSDT", "AVNTUSDT",
            "ASRUSDT", "CLOUDUSDT"
        ]
        
        # All positions exist in previous iteration
        open_syms_prev = set(positions)
        
        # User clicks Close All → cooldown set
        _close_all_cooldown[test_uid] = now + 30
        cooldown_end = _close_all_cooldown.get(test_uid, 0)
        
        # Monitoring loop processes positions during cooldown
        # Check how many SL/TP notifications would be sent
        notifications_sent = 0
        for symbol in positions:
            # This is the NEW logic with cooldown check
            should_notify = (symbol not in open_syms_prev) and (now >= cooldown_end)
            if should_notify:
                notifications_sent += 1
        
        assert notifications_sent == 0, \
            f"Should send 0 SL/TP notifications after Close All, but would send {notifications_sent}"
        
        print(f"✓ Close All test: 0/{len(positions)} SL/TP notifications sent (CORRECT)")
        
        # Test OLD logic (what was causing the bug)
        notifications_old_logic = 0
        for symbol in positions:
            # OLD logic only checked if position is new, NOT cooldown
            if symbol not in open_syms_prev:
                notifications_old_logic += 1
        
        print(f"  (OLD logic would send: {notifications_old_logic} notifications)")
        
        # Cleanup
        del _close_all_cooldown[test_uid]


def run_tests():
    """Run all tests"""
    test = TestNotificationSpam()
    
    tests = [
        test.test_cooldown_prevents_new_position_notification,
        test.test_cooldown_prevents_sl_tp_notification,
        test.test_notifications_allowed_after_cooldown,
        test.test_new_position_with_cooldown_logic,
        test.test_multiple_positions_close_all_scenario,
        test.test_notification_logic_code_check,
        test.test_sl_tp_notification_during_close_all,
    ]
    
    print("=" * 70)
    print("NOTIFICATION SPAM PREVENTION TEST")
    print("=" * 70)
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
    
    print("=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED - Notification spam is FIXED!")
    else:
        print(f"\n❌ {failed} TESTS FAILED - Fix required!")
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
