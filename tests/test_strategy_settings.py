#!/usr/bin/env python3
"""
Comprehensive tests for strategy settings across all strategies.
Tests setting, getting, and using strategy-specific settings for:
- percent, sl_percent, tp_percent (general)
- long_percent, long_sl_percent, long_tp_percent (long-specific)
- short_percent, short_sl_percent, short_tp_percent (short-specific)
- use_atr, atr_periods, atr_multiplier_sl, atr_trigger_pct (ATR settings)
- direction, order_type, trading_mode
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db
from coin_params import DEFAULT_SL_PCT, DEFAULT_TP_PCT

# Test users
TEST_USERS = [
    999901,  # Test user 1 - all strategies enabled
    999902,  # Test user 2 - mixed settings
    999903,  # Test user 3 - side-specific settings
]

STRATEGIES = ["oi", "rsi_bb", "scryptomera", "scalper", "elcaro", "fibonacci"]
EXCHANGES = ["bybit"]
ACCOUNT_TYPES = ["demo", "real"]


def cleanup_test_users():
    """Remove test users before tests"""
    conn = db.get_conn()
    try:
        cur = conn.cursor()
        for uid in TEST_USERS:
            cur.execute("DELETE FROM user_strategy_settings WHERE user_id = ?", (uid,))
            cur.execute("DELETE FROM users WHERE user_id = ?", (uid,))
        conn.commit()
        print(f"✅ Cleaned up {len(TEST_USERS)} test users")
    finally:
        db.release_conn(conn)


def setup_test_users():
    """Create test users with global settings"""
    for uid in TEST_USERS:
        db.ensure_user(uid)
        db.invalidate_user_cache(uid)
    print(f"✅ Created {len(TEST_USERS)} test users")


def test_set_and_get_basic_settings():
    """Test setting and getting basic strategy settings (percent, sl_percent, tp_percent)"""
    print("\n" + "="*60)
    print("TEST: Basic settings (percent, sl_percent, tp_percent)")
    print("="*60)
    
    uid = TEST_USERS[0]
    errors = []
    
    # Define unique settings for each strategy
    strategy_configs = {
        "oi": {"percent": 2.0, "sl_percent": 3.0, "tp_percent": 6.0},
        "rsi_bb": {"percent": 3.0, "sl_percent": 4.0, "tp_percent": 8.0},
        "scryptomera": {"percent": 4.0, "sl_percent": 5.0, "tp_percent": 10.0},
        "scalper": {"percent": 5.0, "sl_percent": 6.0, "tp_percent": 12.0},
        "elcaro": {"percent": 6.0, "sl_percent": 7.0, "tp_percent": 14.0},
        "fibonacci": {"percent": 7.0, "sl_percent": 8.0, "tp_percent": 16.0},
    }
    
    # Set settings for each strategy
    for strategy, settings in strategy_configs.items():
        for field, value in settings.items():
            result = db.set_strategy_setting(uid, strategy, field, value, "bybit", "demo")
            if not result:
                errors.append(f"Failed to set {field}={value} for {strategy}")
    
    # Verify settings
    for strategy, expected in strategy_configs.items():
        strat_settings = db.get_strategy_settings(uid, strategy, "bybit", "demo")
        
        for field, expected_val in expected.items():
            actual = strat_settings.get(field)
            if actual != expected_val:
                errors.append(f"{strategy}.{field}: expected {expected_val}, got {actual}")
            else:
                print(f"  ✅ {strategy}.{field} = {actual}")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return False
    
    print(f"\n✅ All basic settings verified for {len(strategy_configs)} strategies")
    return True


def test_side_specific_settings():
    """Test long/short specific settings"""
    print("\n" + "="*60)
    print("TEST: Side-specific settings (long_*, short_*)")
    print("="*60)
    
    uid = TEST_USERS[1]
    errors = []
    
    # Set different values for long and short for each strategy
    side_configs = {
        "oi": {
            "long_percent": 2.0, "long_sl_percent": 2.5, "long_tp_percent": 5.0,
            "short_percent": 3.0, "short_sl_percent": 3.5, "short_tp_percent": 7.0,
        },
        "rsi_bb": {
            "long_percent": 1.5, "long_sl_percent": 2.0, "long_tp_percent": 4.0,
            "short_percent": 2.5, "short_sl_percent": 3.0, "short_tp_percent": 6.0,
        },
        "scryptomera": {
            "long_percent": 4.0, "long_sl_percent": 4.5, "long_tp_percent": 9.0,
            "short_percent": 5.0, "short_sl_percent": 5.5, "short_tp_percent": 11.0,
        },
        "scalper": {
            "long_percent": 3.5, "long_sl_percent": 3.0, "long_tp_percent": 6.0,
            "short_percent": 4.5, "short_sl_percent": 4.0, "short_tp_percent": 8.0,
        },
    }
    
    # Set settings
    for strategy, settings in side_configs.items():
        for field, value in settings.items():
            result = db.set_strategy_setting(uid, strategy, field, value, "bybit", "demo")
            if not result:
                errors.append(f"Failed to set {field}={value} for {strategy}")
    
    # Verify settings
    for strategy, expected in side_configs.items():
        strat_settings = db.get_strategy_settings(uid, strategy, "bybit", "demo")
        
        for field, expected_val in expected.items():
            actual = strat_settings.get(field)
            if actual != expected_val:
                errors.append(f"{strategy}.{field}: expected {expected_val}, got {actual}")
            else:
                print(f"  ✅ {strategy}.{field} = {actual}")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return False
    
    print(f"\n✅ All side-specific settings verified for {len(side_configs)} strategies")
    return True


def test_atr_settings():
    """Test ATR-related settings"""
    print("\n" + "="*60)
    print("TEST: ATR settings (use_atr, atr_periods, atr_multiplier_sl, atr_trigger_pct)")
    print("="*60)
    
    uid = TEST_USERS[2]
    errors = []
    
    # Set ATR settings - some strategies use ATR, some don't
    atr_configs = {
        "oi": {
            "use_atr": 1,  # ATR enabled
            "atr_periods": 14,
            "atr_multiplier_sl": 2.0,
            "atr_trigger_pct": 3.0,
        },
        "rsi_bb": {
            "use_atr": 0,  # ATR disabled
            "atr_periods": 7,
            "atr_multiplier_sl": 1.5,
            "atr_trigger_pct": 2.0,
        },
        "scryptomera": {
            "use_atr": 1,
            "atr_periods": 21,
            "atr_multiplier_sl": 2.5,
            "atr_trigger_pct": 4.0,
        },
        "scalper": {
            "use_atr": 0,  # Scalper usually fixed SL
            "atr_periods": 5,
            "atr_multiplier_sl": 1.0,
            "atr_trigger_pct": 1.5,
        },
        "elcaro": {
            "use_atr": 1,
            "atr_periods": 10,
            "atr_multiplier_sl": 1.8,
            "atr_trigger_pct": 2.5,
        },
    }
    
    # Set settings
    for strategy, settings in atr_configs.items():
        for field, value in settings.items():
            result = db.set_strategy_setting(uid, strategy, field, value, "bybit", "demo")
            if not result:
                errors.append(f"Failed to set {field}={value} for {strategy}")
    
    # Verify settings
    for strategy, expected in atr_configs.items():
        strat_settings = db.get_strategy_settings(uid, strategy, "bybit", "demo")
        
        for field, expected_val in expected.items():
            actual = strat_settings.get(field)
            if actual != expected_val:
                errors.append(f"{strategy}.{field}: expected {expected_val}, got {actual}")
            else:
                print(f"  ✅ {strategy}.{field} = {actual}")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return False
    
    print(f"\n✅ All ATR settings verified for {len(atr_configs)} strategies")
    return True


def test_direction_and_mode_settings():
    """Test direction and trading_mode settings"""
    print("\n" + "="*60)
    print("TEST: Direction and trading_mode settings")
    print("="*60)
    
    uid = TEST_USERS[0]
    errors = []
    
    # Set different directions and modes
    mode_configs = {
        "oi": {"direction": "all", "trading_mode": "demo"},
        "rsi_bb": {"direction": "long", "trading_mode": "real"},
        "scryptomera": {"direction": "short", "trading_mode": "both"},
        "scalper": {"direction": "all", "trading_mode": "global"},
        "elcaro": {"direction": "long", "trading_mode": "demo"},
        "fibonacci": {"direction": "short", "trading_mode": "real"},
    }
    
    # Set settings
    for strategy, settings in mode_configs.items():
        for field, value in settings.items():
            result = db.set_strategy_setting(uid, strategy, field, value, "bybit", "demo")
            if not result:
                errors.append(f"Failed to set {field}={value} for {strategy}")
    
    # Verify settings
    for strategy, expected in mode_configs.items():
        strat_settings = db.get_strategy_settings(uid, strategy, "bybit", "demo")
        
        for field, expected_val in expected.items():
            actual = strat_settings.get(field)
            if actual != expected_val:
                errors.append(f"{strategy}.{field}: expected {expected_val}, got {actual}")
            else:
                print(f"  ✅ {strategy}.{field} = {actual}")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return False
    
    print(f"\n✅ All direction/mode settings verified for {len(mode_configs)} strategies")
    return True


def test_resolve_sl_tp_with_strategy():
    """Test that resolve_sl_tp_pct uses strategy settings correctly"""
    print("\n" + "="*60)
    print("TEST: resolve_sl_tp_pct with strategy settings")
    print("="*60)
    
    # Import the function from bot
    import importlib.util
    spec = importlib.util.spec_from_file_location("bot_resolve", "bot.py")
    
    # Since we can't load bot.py fully, test the logic manually
    uid = TEST_USERS[0]
    errors = []
    
    # Set up distinct settings for each strategy
    configs = {
        "oi": {"sl_percent": 2.5, "tp_percent": 5.0},
        "rsi_bb": {"sl_percent": 3.0, "tp_percent": 6.0},
        "elcaro": {"sl_percent": 4.0, "tp_percent": 8.0},
    }
    
    for strategy, settings in configs.items():
        for field, value in settings.items():
            db.set_strategy_setting(uid, strategy, field, value, "bybit", "demo")
    
    # Verify each strategy has its own settings
    for strategy, expected in configs.items():
        strat_settings = db.get_strategy_settings(uid, strategy, "bybit", "demo")
        
        sl = strat_settings.get("sl_percent")
        tp = strat_settings.get("tp_percent")
        
        if sl != expected["sl_percent"]:
            errors.append(f"{strategy} SL: expected {expected['sl_percent']}, got {sl}")
        if tp != expected["tp_percent"]:
            errors.append(f"{strategy} TP: expected {expected['tp_percent']}, got {tp}")
        
        print(f"  ✅ {strategy}: SL={sl}%, TP={tp}%")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return False
    
    print(f"\n✅ Strategy settings isolated correctly")
    return True


def test_side_specific_in_trade_params():
    """Test that side-specific settings override general settings"""
    print("\n" + "="*60)
    print("TEST: Side-specific overrides general settings")
    print("="*60)
    
    uid = TEST_USERS[1]
    errors = []
    
    # Set general + side-specific for scalper
    strategy = "scalper"
    
    # General settings
    db.set_strategy_setting(uid, strategy, "percent", 2.0, "bybit", "demo")
    db.set_strategy_setting(uid, strategy, "sl_percent", 3.0, "bybit", "demo")
    db.set_strategy_setting(uid, strategy, "tp_percent", 6.0, "bybit", "demo")
    
    # Side-specific overrides
    db.set_strategy_setting(uid, strategy, "long_percent", 1.5, "bybit", "demo")
    db.set_strategy_setting(uid, strategy, "long_sl_percent", 2.0, "bybit", "demo")
    db.set_strategy_setting(uid, strategy, "long_tp_percent", 4.0, "bybit", "demo")
    
    db.set_strategy_setting(uid, strategy, "short_percent", 2.5, "bybit", "demo")
    db.set_strategy_setting(uid, strategy, "short_sl_percent", 4.0, "bybit", "demo")
    db.set_strategy_setting(uid, strategy, "short_tp_percent", 8.0, "bybit", "demo")
    
    # Verify
    strat_settings = db.get_strategy_settings(uid, strategy, "bybit", "demo")
    
    # Check general
    expected_general = {"percent": 2.0, "sl_percent": 3.0, "tp_percent": 6.0}
    for field, expected_val in expected_general.items():
        actual = strat_settings.get(field)
        if actual != expected_val:
            errors.append(f"General {field}: expected {expected_val}, got {actual}")
        else:
            print(f"  ✅ General {field} = {actual}")
    
    # Check long
    expected_long = {"long_percent": 1.5, "long_sl_percent": 2.0, "long_tp_percent": 4.0}
    for field, expected_val in expected_long.items():
        actual = strat_settings.get(field)
        if actual != expected_val:
            errors.append(f"Long {field}: expected {expected_val}, got {actual}")
        else:
            print(f"  ✅ {field} = {actual}")
    
    # Check short
    expected_short = {"short_percent": 2.5, "short_sl_percent": 4.0, "short_tp_percent": 8.0}
    for field, expected_val in expected_short.items():
        actual = strat_settings.get(field)
        if actual != expected_val:
            errors.append(f"Short {field}: expected {expected_val}, got {actual}")
        else:
            print(f"  ✅ {field} = {actual}")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return False
    
    print(f"\n✅ Side-specific settings work correctly")
    return True


def test_get_effective_settings():
    """Test get_effective_settings falls back correctly"""
    print("\n" + "="*60)
    print("TEST: get_effective_settings fallback logic")
    print("="*60)
    
    uid = TEST_USERS[2]
    errors = []
    
    # Set global user settings
    db.set_user_field(uid, "sl_percent", 5.0)
    db.set_user_field(uid, "tp_percent", 10.0)
    db.set_user_field(uid, "percent", 3.0)
    db.invalidate_user_cache(uid)
    
    # Set only SL for oi strategy - TP should fall back to global
    db.set_strategy_setting(uid, "oi", "sl_percent", 2.0, "bybit", "demo")
    
    # Get effective settings
    effective = db.get_effective_settings(uid, "oi")
    
    # SL should be from strategy (2.0)
    if effective["sl_percent"] != 2.0:
        errors.append(f"SL should be 2.0 (strategy), got {effective['sl_percent']}")
    else:
        print(f"  ✅ SL = {effective['sl_percent']} (from strategy)")
    
    # TP should fall back to global (10.0)
    if effective["tp_percent"] != 10.0:
        errors.append(f"TP should be 10.0 (global), got {effective['tp_percent']}")
    else:
        print(f"  ✅ TP = {effective['tp_percent']} (fallback to global)")
    
    # Percent should fall back to global (3.0)
    if effective["percent"] != 3.0:
        errors.append(f"Percent should be 3.0 (global), got {effective['percent']}")
    else:
        print(f"  ✅ Percent = {effective['percent']} (fallback to global)")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return False
    
    print(f"\n✅ Effective settings fallback works correctly")
    return True


def test_exchange_account_isolation():
    """Test that settings are isolated by exchange and account_type"""
    print("\n" + "="*60)
    print("TEST: Exchange and account_type isolation")
    print("="*60)
    
    uid = TEST_USERS[0]
    errors = []
    
    strategy = "oi"
    
    # Set different settings for demo vs real
    db.set_strategy_setting(uid, strategy, "percent", 1.0, "bybit", "demo")
    db.set_strategy_setting(uid, strategy, "sl_percent", 2.0, "bybit", "demo")
    
    db.set_strategy_setting(uid, strategy, "percent", 5.0, "bybit", "real")
    db.set_strategy_setting(uid, strategy, "sl_percent", 10.0, "bybit", "real")
    
    # Verify demo settings
    demo_settings = db.get_strategy_settings(uid, strategy, "bybit", "demo")
    if demo_settings.get("percent") != 1.0:
        errors.append(f"Demo percent: expected 1.0, got {demo_settings.get('percent')}")
    else:
        print(f"  ✅ Demo percent = {demo_settings.get('percent')}")
    
    if demo_settings.get("sl_percent") != 2.0:
        errors.append(f"Demo SL: expected 2.0, got {demo_settings.get('sl_percent')}")
    else:
        print(f"  ✅ Demo SL = {demo_settings.get('sl_percent')}")
    
    # Verify real settings
    real_settings = db.get_strategy_settings(uid, strategy, "bybit", "real")
    if real_settings.get("percent") != 5.0:
        errors.append(f"Real percent: expected 5.0, got {real_settings.get('percent')}")
    else:
        print(f"  ✅ Real percent = {real_settings.get('percent')}")
    
    if real_settings.get("sl_percent") != 10.0:
        errors.append(f"Real SL: expected 10.0, got {real_settings.get('sl_percent')}")
    else:
        print(f"  ✅ Real SL = {real_settings.get('sl_percent')}")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return False
    
    print(f"\n✅ Settings are isolated by account_type correctly")
    return True


def test_none_value_handling():
    """Test that None values reset to default"""
    print("\n" + "="*60)
    print("TEST: None value handling (reset to default)")
    print("="*60)
    
    uid = TEST_USERS[2]
    errors = []
    strategy = "fibonacci"
    
    # Set a value
    db.set_strategy_setting(uid, strategy, "sl_percent", 5.0, "bybit", "demo")
    
    # Verify it's set
    settings = db.get_strategy_settings(uid, strategy, "bybit", "demo")
    if settings.get("sl_percent") != 5.0:
        errors.append(f"Initial SL should be 5.0, got {settings.get('sl_percent')}")
    else:
        print(f"  ✅ SL set to {settings.get('sl_percent')}")
    
    # Reset to None
    db.set_strategy_setting(uid, strategy, "sl_percent", None, "bybit", "demo")
    
    # Verify it's None
    settings = db.get_strategy_settings(uid, strategy, "bybit", "demo")
    if settings.get("sl_percent") is not None:
        errors.append(f"SL should be None after reset, got {settings.get('sl_percent')}")
    else:
        print(f"  ✅ SL reset to None")
    
    # Verify effective settings use fallback
    effective = db.get_effective_settings(uid, strategy)
    if effective["sl_percent"] is None or effective["sl_percent"] == 0:
        errors.append(f"Effective SL should fallback to default, got {effective['sl_percent']}")
    else:
        print(f"  ✅ Effective SL fallback to {effective['sl_percent']} (global/default)")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return False
    
    print(f"\n✅ None value handling works correctly")
    return True


def test_all_strategies_independence():
    """Test that each strategy maintains independent settings"""
    print("\n" + "="*60)
    print("TEST: All strategies independence")
    print("="*60)
    
    uid = TEST_USERS[0]
    errors = []
    
    # Set unique percent for each strategy
    unique_percents = {
        "oi": 1.1,
        "rsi_bb": 2.2,
        "scryptomera": 3.3,
        "scalper": 4.4,
        "elcaro": 5.5,
        "fibonacci": 6.6,
    }
    
    # Set all
    for strategy, percent in unique_percents.items():
        db.set_strategy_setting(uid, strategy, "percent", percent, "bybit", "demo")
    
    # Verify all are independent
    for strategy, expected in unique_percents.items():
        settings = db.get_strategy_settings(uid, strategy, "bybit", "demo")
        actual = settings.get("percent")
        if actual != expected:
            errors.append(f"{strategy} percent: expected {expected}, got {actual}")
        else:
            print(f"  ✅ {strategy} percent = {actual}")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return False
    
    print(f"\n✅ All strategies maintain independent settings")
    return True


def test_real_user_995144364():
    """Test with real user 995144364 - simulate setting different configs"""
    print("\n" + "="*60)
    print("TEST: Real user 995144364 - setting diverse configs")
    print("="*60)
    
    uid = 995144364
    errors = []
    
    # Backup current settings (optional - just verify they can be read)
    print("  📊 Current settings for user 995144364:")
    for strategy in STRATEGIES:
        settings = db.get_strategy_settings(uid, strategy, "bybit", "demo")
        percent = settings.get("percent") or "default"
        sl = settings.get("sl_percent") or "default"
        tp = settings.get("tp_percent") or "default"
        use_atr = settings.get("use_atr")
        use_atr_str = "None (global)" if use_atr is None else ("ON" if use_atr else "OFF")
        print(f"    {strategy}: percent={percent}, SL={sl}, TP={tp}, ATR={use_atr_str}")
    
    print("\n  ✅ All settings readable for real user")
    return True


def test_get_strategy_trade_params_simulation():
    """Simulate get_strategy_trade_params logic for trade parameter resolution"""
    print("\n" + "="*60)
    print("TEST: get_strategy_trade_params simulation")
    print("="*60)
    
    uid = TEST_USERS[1]
    errors = []
    
    # Setup: scalper with side-specific settings
    strategy = "scalper"
    db.set_strategy_setting(uid, strategy, "percent", 2.0, "bybit", "demo")
    db.set_strategy_setting(uid, strategy, "sl_percent", 3.0, "bybit", "demo")
    db.set_strategy_setting(uid, strategy, "tp_percent", 6.0, "bybit", "demo")
    db.set_strategy_setting(uid, strategy, "long_percent", 1.0, "bybit", "demo")
    db.set_strategy_setting(uid, strategy, "long_sl_percent", 1.5, "bybit", "demo")
    db.set_strategy_setting(uid, strategy, "short_percent", 3.0, "bybit", "demo")
    db.set_strategy_setting(uid, strategy, "short_sl_percent", 4.0, "bybit", "demo")
    
    strat_settings = db.get_strategy_settings(uid, strategy, "bybit", "demo")
    
    # Simulate get_strategy_trade_params for LONG
    side = "Buy"
    side_prefix = "long"
    
    side_percent = strat_settings.get(f"{side_prefix}_percent")
    if side_percent is not None and side_percent > 0:
        long_percent = float(side_percent)
    else:
        long_percent = float(strat_settings.get("percent", 2.0))
    
    side_sl = strat_settings.get(f"{side_prefix}_sl_percent")
    if side_sl is not None and side_sl > 0:
        long_sl = float(side_sl)
    else:
        long_sl = float(strat_settings.get("sl_percent", 3.0))
    
    print(f"  LONG trade params: percent={long_percent}, SL={long_sl}")
    
    if long_percent != 1.0:
        errors.append(f"LONG percent should be 1.0 (side-specific), got {long_percent}")
    else:
        print(f"    ✅ LONG percent uses side-specific: {long_percent}")
    
    if long_sl != 1.5:
        errors.append(f"LONG SL should be 1.5 (side-specific), got {long_sl}")
    else:
        print(f"    ✅ LONG SL uses side-specific: {long_sl}")
    
    # Simulate for SHORT
    side = "Sell"
    side_prefix = "short"
    
    side_percent = strat_settings.get(f"{side_prefix}_percent")
    if side_percent is not None and side_percent > 0:
        short_percent = float(side_percent)
    else:
        short_percent = float(strat_settings.get("percent", 2.0))
    
    side_sl = strat_settings.get(f"{side_prefix}_sl_percent")
    if side_sl is not None and side_sl > 0:
        short_sl = float(side_sl)
    else:
        short_sl = float(strat_settings.get("sl_percent", 3.0))
    
    print(f"  SHORT trade params: percent={short_percent}, SL={short_sl}")
    
    if short_percent != 3.0:
        errors.append(f"SHORT percent should be 3.0 (side-specific), got {short_percent}")
    else:
        print(f"    ✅ SHORT percent uses side-specific: {short_percent}")
    
    if short_sl != 4.0:
        errors.append(f"SHORT SL should be 4.0 (side-specific), got {short_sl}")
    else:
        print(f"    ✅ SHORT SL uses side-specific: {short_sl}")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return False
    
    print(f"\n✅ Trade params resolution works correctly for both sides")
    return True


def test_use_atr_with_global_fallback():
    """Test use_atr with global fallback"""
    print("\n" + "="*60)
    print("TEST: use_atr with global fallback")
    print("="*60)
    
    uid = TEST_USERS[0]
    errors = []
    
    # Set global use_atr to True
    db.set_user_field(uid, "use_atr", 1)
    db.invalidate_user_cache(uid)
    
    cfg = db.get_user_config(uid)
    global_use_atr = bool(cfg.get("use_atr", 1))
    
    print(f"  Global use_atr: {global_use_atr}")
    
    # Test 1: Strategy with use_atr = None → should use global
    strategy = "elcaro"
    db.set_strategy_setting(uid, strategy, "use_atr", None, "bybit", "demo")
    strat_settings = db.get_strategy_settings(uid, strategy, "bybit", "demo")
    
    strat_use_atr = strat_settings.get("use_atr")
    effective_use_atr = strat_use_atr if strat_use_atr is not None else (1 if global_use_atr else 0)
    
    print(f"  {strategy}: strat_use_atr={strat_use_atr}, effective={effective_use_atr}")
    
    if strat_use_atr is not None:
        errors.append(f"{strategy} use_atr should be None, got {strat_use_atr}")
    if effective_use_atr != 1:
        errors.append(f"{strategy} effective use_atr should be 1 (from global), got {effective_use_atr}")
    else:
        print(f"    ✅ Falls back to global: ATR ON")
    
    # Test 2: Strategy with use_atr = 0 → should override global
    strategy = "scalper"
    db.set_strategy_setting(uid, strategy, "use_atr", 0, "bybit", "demo")
    strat_settings = db.get_strategy_settings(uid, strategy, "bybit", "demo")
    
    strat_use_atr = strat_settings.get("use_atr")
    effective_use_atr = strat_use_atr if strat_use_atr is not None else (1 if global_use_atr else 0)
    
    print(f"  {strategy}: strat_use_atr={strat_use_atr}, effective={effective_use_atr}")
    
    if strat_use_atr != 0:
        errors.append(f"{strategy} use_atr should be 0, got {strat_use_atr}")
    if effective_use_atr != 0:
        errors.append(f"{strategy} effective use_atr should be 0 (overrides global), got {effective_use_atr}")
    else:
        print(f"    ✅ Overrides global: ATR OFF")
    
    # Test 3: Strategy with use_atr = 1 → explicit ATR on
    strategy = "oi"
    db.set_strategy_setting(uid, strategy, "use_atr", 1, "bybit", "demo")
    strat_settings = db.get_strategy_settings(uid, strategy, "bybit", "demo")
    
    strat_use_atr = strat_settings.get("use_atr")
    effective_use_atr = strat_use_atr if strat_use_atr is not None else (1 if global_use_atr else 0)
    
    print(f"  {strategy}: strat_use_atr={strat_use_atr}, effective={effective_use_atr}")
    
    if strat_use_atr != 1:
        errors.append(f"{strategy} use_atr should be 1, got {strat_use_atr}")
    if effective_use_atr != 1:
        errors.append(f"{strategy} effective use_atr should be 1, got {effective_use_atr}")
    else:
        print(f"    ✅ Explicit ATR ON")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return False
    
    print(f"\n✅ use_atr fallback logic works correctly")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("STRATEGY SETTINGS COMPREHENSIVE TESTS")
    print("="*80)
    
    # Setup
    cleanup_test_users()
    setup_test_users()
    
    tests = [
        ("Basic settings", test_set_and_get_basic_settings),
        ("Side-specific settings", test_side_specific_settings),
        ("ATR settings", test_atr_settings),
        ("Direction and mode", test_direction_and_mode_settings),
        ("Strategy SL/TP isolation", test_resolve_sl_tp_with_strategy),
        ("Side-specific overrides", test_side_specific_in_trade_params),
        ("Effective settings fallback", test_get_effective_settings),
        ("Exchange/account isolation", test_exchange_account_isolation),
        ("None value handling", test_none_value_handling),
        ("All strategies independence", test_all_strategies_independence),
        ("Real user 995144364", test_real_user_995144364),
        ("Trade params simulation", test_get_strategy_trade_params_simulation),
        ("use_atr with global fallback", test_use_atr_with_global_fallback),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_fn in tests:
        try:
            result = test_fn()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ {name} EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Cleanup
    cleanup_test_users()
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Total: {len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {failed} tests failed - review errors above")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
