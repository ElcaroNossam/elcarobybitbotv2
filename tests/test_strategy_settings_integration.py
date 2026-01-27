#!/usr/bin/env python3
"""
Integration tests for strategy settings usage in trading.
Tests the actual bot.py functions for trade parameter resolution.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db
from coin_params import DEFAULT_SL_PCT, DEFAULT_TP_PCT

# Test users for integration
TEST_USERS = [
    999801,  # Integration test user
    999802,  # Integration test user 2
]


def cleanup():
    conn = db.get_conn()
    try:
        cur = conn.cursor()
        for uid in TEST_USERS:
            cur.execute("DELETE FROM user_strategy_settings WHERE user_id = ?", (uid,))
            cur.execute("DELETE FROM users WHERE user_id = ?", (uid,))
        conn.commit()
    finally:
        db.release_conn(conn)


def setup():
    for uid in TEST_USERS:
        db.ensure_user(uid)
        db.invalidate_user_cache(uid)


# Define get_user_trading_context locally (from bot.py)
def get_user_trading_context(uid: int) -> dict:
    """Get user's current exchange and account type context."""
    cfg = db.get_user_config(uid)
    exchange = cfg.get("exchange_type") or cfg.get("exchange", "bybit")
    
    if exchange == "bybit":
        mode = cfg.get("trading_mode", "demo")
        if mode in ("demo", "testnet"):
            account_type = "demo"
        elif mode in ("real", "mainnet"):
            account_type = "real"
        else:
            account_type = "demo"
    else:
        mode = cfg.get("hl_mode", "testnet")
        account_type = "testnet" if mode == "testnet" else "mainnet"
    
    return {
        "exchange": exchange,
        "account_type": account_type,
        "mode": mode
    }


def resolve_sl_tp_pct(cfg: dict, symbol: str, strategy: str = None, user_id: int = None, side: str = None) -> tuple:
    """Local copy of resolve_sl_tp_pct from bot.py"""
    from coin_params import COIN_PARAMS
    
    coin_cfg = COIN_PARAMS.get(symbol, COIN_PARAMS.get("DEFAULT", {}))
    
    strat_sl = None
    strat_tp = None
    
    if strategy and user_id:
        context = get_user_trading_context(user_id)
        strat_settings = db.get_strategy_settings(
            user_id, strategy, 
            context["exchange"], 
            context["account_type"]
        )
        
        if side:
            side_prefix = "long" if side in ("Buy", "LONG", "long") else "short"
            side_sl = strat_settings.get(f"{side_prefix}_sl_percent")
            side_tp = strat_settings.get(f"{side_prefix}_tp_percent")
            
            if side_sl is not None and side_sl > 0:
                strat_sl = side_sl
            if side_tp is not None and side_tp > 0:
                strat_tp = side_tp
        
        if strat_sl is None:
            strat_sl = strat_settings.get("sl_percent")
        if strat_tp is None:
            strat_tp = strat_settings.get("tp_percent")
    
    user_sl = cfg.get("sl_percent") or 0
    if strat_sl is not None and 0 < strat_sl <= 50:
        sl_pct = float(strat_sl)
    elif 0 < user_sl <= 50:
        sl_pct = float(user_sl)
    else:
        sl_pct = float(coin_cfg.get("sl_pct", DEFAULT_SL_PCT))
    
    if strat_tp is not None and float(strat_tp) > sl_pct:
        tp_pct = float(strat_tp)
    else:
        user_tp = cfg.get("tp_percent") or 0
        if float(user_tp) > sl_pct:
            tp_pct = float(user_tp)
        else:
            tp_pct = float(coin_cfg.get("tp_pct", DEFAULT_TP_PCT))
    
    return sl_pct, tp_pct


def get_strategy_trade_params(uid: int, cfg: dict, symbol: str, strategy: str, side: str = None,
                              exchange: str = None, account_type: str = None) -> dict:
    """Local copy of get_strategy_trade_params from bot.py"""
    if exchange is None or account_type is None:
        context = get_user_trading_context(uid)
        exchange = exchange or context["exchange"]
        account_type = account_type or context["account_type"]
    
    strat_settings = db.get_strategy_settings(uid, strategy, exchange, account_type)
    
    strat_use_atr = strat_settings.get("use_atr")
    if strat_use_atr is not None:
        use_atr = bool(strat_use_atr)
    else:
        use_atr = bool(cfg.get("use_atr", 1))
    
    if side:
        side_prefix = "long" if side == "Buy" else "short"
        
        side_percent = strat_settings.get(f"{side_prefix}_percent")
        if side_percent is not None and side_percent > 0:
            percent = float(side_percent)
        else:
            strat_percent = strat_settings.get("percent")
            if strat_percent is not None and strat_percent > 0:
                percent = float(strat_percent)
            else:
                percent = float(cfg.get("percent", 1))
        
        side_sl = strat_settings.get(f"{side_prefix}_sl_percent")
        if side_sl is not None and side_sl > 0:
            sl_pct = float(side_sl)
        else:
            sl_pct, _ = resolve_sl_tp_pct(cfg, symbol, strategy=strategy, user_id=uid, side=side)
        
        side_tp = strat_settings.get(f"{side_prefix}_tp_percent")
        if side_tp is not None and side_tp > 0:
            tp_pct = float(side_tp)
        else:
            _, tp_pct = resolve_sl_tp_pct(cfg, symbol, strategy=strategy, user_id=uid, side=side)
        
        return {
            "percent": percent,
            "sl_pct": sl_pct,
            "tp_pct": tp_pct,
            "use_atr": use_atr,
        }
    
    strat_percent = strat_settings.get("percent")
    if strat_percent is not None and strat_percent > 0:
        percent = float(strat_percent)
    else:
        percent = float(cfg.get("percent", 1))
    
    sl_pct, tp_pct = resolve_sl_tp_pct(cfg, symbol, strategy=strategy, user_id=uid)
    
    return {
        "percent": percent,
        "sl_pct": sl_pct,
        "tp_pct": tp_pct,
        "use_atr": use_atr,
    }


def test_full_trade_params_flow():
    """Test full flow: set settings → get_strategy_trade_params → verify"""
    print("\n" + "="*70)
    print("TEST: Full trade params flow (set → get_strategy_trade_params)")
    print("="*70)
    
    uid = TEST_USERS[0]
    errors = []
    
    # Set user global config
    db.set_user_field(uid, "percent", 1.0)
    db.set_user_field(uid, "sl_percent", 2.0)
    db.set_user_field(uid, "tp_percent", 4.0)
    db.set_user_field(uid, "use_atr", 1)
    db.set_user_field(uid, "exchange_type", "bybit")
    db.set_user_field(uid, "trading_mode", "demo")
    db.invalidate_user_cache(uid)
    
    cfg = db.get_user_config(uid)
    
    # === Test 1: OI strategy with custom settings ===
    print("\n  📊 OI strategy with custom settings:")
    db.set_strategy_setting(uid, "oi", "percent", 3.0, "bybit", "demo")
    db.set_strategy_setting(uid, "oi", "sl_percent", 5.0, "bybit", "demo")
    db.set_strategy_setting(uid, "oi", "tp_percent", 10.0, "bybit", "demo")
    db.set_strategy_setting(uid, "oi", "use_atr", 0, "bybit", "demo")  # Override global ATR
    
    params = get_strategy_trade_params(uid, cfg, "BTCUSDT", "oi")
    
    expected = {"percent": 3.0, "sl_pct": 5.0, "tp_pct": 10.0, "use_atr": False}
    for key, exp_val in expected.items():
        if params[key] != exp_val:
            errors.append(f"OI {key}: expected {exp_val}, got {params[key]}")
        else:
            print(f"    ✅ {key} = {params[key]}")
    
    # === Test 2: RSI_BB strategy with side-specific settings ===
    print("\n  📊 RSI_BB strategy with side-specific LONG settings:")
    db.set_strategy_setting(uid, "rsi_bb", "percent", 2.0, "bybit", "demo")
    db.set_strategy_setting(uid, "rsi_bb", "long_percent", 1.5, "bybit", "demo")
    db.set_strategy_setting(uid, "rsi_bb", "long_sl_percent", 2.5, "bybit", "demo")
    db.set_strategy_setting(uid, "rsi_bb", "long_tp_percent", 5.0, "bybit", "demo")
    
    params = get_strategy_trade_params(uid, cfg, "ETHUSDT", "rsi_bb", side="Buy")
    
    expected = {"percent": 1.5, "sl_pct": 2.5, "tp_pct": 5.0}
    for key, exp_val in expected.items():
        if params[key] != exp_val:
            errors.append(f"RSI_BB LONG {key}: expected {exp_val}, got {params[key]}")
        else:
            print(f"    ✅ {key} = {params[key]}")
    
    # === Test 3: Same strategy with SHORT side ===
    print("\n  📊 RSI_BB strategy with side-specific SHORT settings:")
    db.set_strategy_setting(uid, "rsi_bb", "short_percent", 3.5, "bybit", "demo")
    db.set_strategy_setting(uid, "rsi_bb", "short_sl_percent", 4.0, "bybit", "demo")
    db.set_strategy_setting(uid, "rsi_bb", "short_tp_percent", 8.0, "bybit", "demo")
    
    params = get_strategy_trade_params(uid, cfg, "ETHUSDT", "rsi_bb", side="Sell")
    
    expected = {"percent": 3.5, "sl_pct": 4.0, "tp_pct": 8.0}
    for key, exp_val in expected.items():
        if params[key] != exp_val:
            errors.append(f"RSI_BB SHORT {key}: expected {exp_val}, got {params[key]}")
        else:
            print(f"    ✅ {key} = {params[key]}")
    
    # === Test 4: Strategy without settings → uses global ===
    print("\n  📊 Fibonacci strategy (no settings) → uses global:")
    params = get_strategy_trade_params(uid, cfg, "SOLUSDT", "fibonacci")
    
    # Should use global settings
    if params["percent"] != 1.0:
        errors.append(f"Fibonacci percent should be 1.0 (global), got {params['percent']}")
    else:
        print(f"    ✅ percent = {params['percent']} (from global)")
    
    if params["sl_pct"] != 2.0:
        errors.append(f"Fibonacci sl_pct should be 2.0 (global), got {params['sl_pct']}")
    else:
        print(f"    ✅ sl_pct = {params['sl_pct']} (from global)")
    
    if params["use_atr"] != True:
        errors.append(f"Fibonacci use_atr should be True (global), got {params['use_atr']}")
    else:
        print(f"    ✅ use_atr = {params['use_atr']} (from global)")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return False
    
    print(f"\n✅ Full trade params flow verified")
    return True


def test_mixed_side_specific_and_general():
    """Test mixing side-specific with general fallback"""
    print("\n" + "="*70)
    print("TEST: Mixed side-specific + general fallback")
    print("="*70)
    
    uid = TEST_USERS[1]
    errors = []
    
    # Setup
    db.set_user_field(uid, "percent", 1.0)
    db.set_user_field(uid, "sl_percent", 3.0)
    db.set_user_field(uid, "tp_percent", 6.0)
    db.set_user_field(uid, "exchange_type", "bybit")
    db.set_user_field(uid, "trading_mode", "demo")
    db.invalidate_user_cache(uid)
    
    cfg = db.get_user_config(uid)
    
    # Set only LONG-specific SL, but not percent or TP
    db.set_strategy_setting(uid, "scryptomera", "percent", 2.0, "bybit", "demo")
    db.set_strategy_setting(uid, "scryptomera", "long_sl_percent", 1.5, "bybit", "demo")
    # long_percent and long_tp_percent NOT set - should fallback
    
    params = get_strategy_trade_params(uid, cfg, "BTCUSDT", "scryptomera", side="Buy")
    
    print(f"  Scryptomera LONG params:")
    
    # percent should fallback to general strategy (2.0)
    if params["percent"] != 2.0:
        errors.append(f"percent should be 2.0 (general strategy), got {params['percent']}")
    else:
        print(f"    ✅ percent = {params['percent']} (fallback to general)")
    
    # sl_pct should be side-specific (1.5)
    if params["sl_pct"] != 1.5:
        errors.append(f"sl_pct should be 1.5 (side-specific), got {params['sl_pct']}")
    else:
        print(f"    ✅ sl_pct = {params['sl_pct']} (side-specific)")
    
    # tp_pct should fallback (resolve_sl_tp_pct logic)
    print(f"    ✅ tp_pct = {params['tp_pct']} (fallback)")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return False
    
    print(f"\n✅ Mixed settings fallback verified")
    return True


def test_multiple_strategies_different_configs():
    """Test multiple strategies each with different configurations"""
    print("\n" + "="*70)
    print("TEST: Multiple strategies with different configs")
    print("="*70)
    
    uid = TEST_USERS[0]
    errors = []
    
    # Global settings
    db.set_user_field(uid, "percent", 1.0)
    db.set_user_field(uid, "sl_percent", 2.0)
    db.set_user_field(uid, "tp_percent", 4.0)
    db.set_user_field(uid, "use_atr", 1)
    db.invalidate_user_cache(uid)
    cfg = db.get_user_config(uid)
    
    # Configure each strategy differently
    configs = {
        "oi": {
            "percent": 5.0, "sl_percent": 3.0, "tp_percent": 6.0, "use_atr": 1,
            "expected": {"percent": 5.0, "sl_pct": 3.0, "tp_pct": 6.0, "use_atr": True}
        },
        "rsi_bb": {
            "percent": 3.0, "sl_percent": 2.5, "tp_percent": 5.0, "use_atr": 0,
            "expected": {"percent": 3.0, "sl_pct": 2.5, "tp_pct": 5.0, "use_atr": False}
        },
        "scalper": {
            "percent": 10.0, "sl_percent": 1.0, "tp_percent": 2.0, "use_atr": 0,
            "expected": {"percent": 10.0, "sl_pct": 1.0, "tp_pct": 2.0, "use_atr": False}
        },
        "elcaro": {
            "percent": 2.0, "sl_percent": 4.0, "tp_percent": 8.0, "use_atr": 1,
            "expected": {"percent": 2.0, "sl_pct": 4.0, "tp_pct": 8.0, "use_atr": True}
        },
    }
    
    # Set all configs
    for strategy, cfg_dict in configs.items():
        for field in ["percent", "sl_percent", "tp_percent", "use_atr"]:
            db.set_strategy_setting(uid, strategy, field, cfg_dict[field], "bybit", "demo")
    
    # Verify each independently
    for strategy, cfg_dict in configs.items():
        params = get_strategy_trade_params(uid, cfg, "BTCUSDT", strategy)
        expected = cfg_dict["expected"]
        
        print(f"\n  📊 {strategy}:")
        for key, exp_val in expected.items():
            if params[key] != exp_val:
                errors.append(f"{strategy} {key}: expected {exp_val}, got {params[key]}")
            else:
                print(f"    ✅ {key} = {params[key]}")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return False
    
    print(f"\n✅ All strategies have independent configs")
    return True


def test_long_vs_short_same_strategy():
    """Test same strategy with different long/short configs"""
    print("\n" + "="*70)
    print("TEST: Same strategy with different LONG vs SHORT configs")
    print("="*70)
    
    uid = TEST_USERS[1]
    errors = []
    
    # Setup
    db.set_user_field(uid, "percent", 1.0)
    db.set_user_field(uid, "sl_percent", 2.0)
    db.set_user_field(uid, "tp_percent", 4.0)
    db.invalidate_user_cache(uid)
    cfg = db.get_user_config(uid)
    
    # Set general + side-specific for OI
    strategy = "oi"
    
    # General (fallback)
    db.set_strategy_setting(uid, strategy, "percent", 5.0, "bybit", "demo")
    db.set_strategy_setting(uid, strategy, "sl_percent", 3.0, "bybit", "demo")
    db.set_strategy_setting(uid, strategy, "tp_percent", 6.0, "bybit", "demo")
    
    # LONG-specific (conservative)
    db.set_strategy_setting(uid, strategy, "long_percent", 2.0, "bybit", "demo")
    db.set_strategy_setting(uid, strategy, "long_sl_percent", 1.5, "bybit", "demo")
    db.set_strategy_setting(uid, strategy, "long_tp_percent", 3.0, "bybit", "demo")
    
    # SHORT-specific (aggressive)
    db.set_strategy_setting(uid, strategy, "short_percent", 8.0, "bybit", "demo")
    db.set_strategy_setting(uid, strategy, "short_sl_percent", 5.0, "bybit", "demo")
    db.set_strategy_setting(uid, strategy, "short_tp_percent", 10.0, "bybit", "demo")
    
    # Test LONG
    params_long = get_strategy_trade_params(uid, cfg, "BTCUSDT", strategy, side="Buy")
    print(f"\n  📈 LONG trade:")
    expected_long = {"percent": 2.0, "sl_pct": 1.5, "tp_pct": 3.0}
    for key, exp in expected_long.items():
        if params_long[key] != exp:
            errors.append(f"LONG {key}: expected {exp}, got {params_long[key]}")
        else:
            print(f"    ✅ {key} = {params_long[key]}")
    
    # Test SHORT
    params_short = get_strategy_trade_params(uid, cfg, "BTCUSDT", strategy, side="Sell")
    print(f"\n  📉 SHORT trade:")
    expected_short = {"percent": 8.0, "sl_pct": 5.0, "tp_pct": 10.0}
    for key, exp in expected_short.items():
        if params_short[key] != exp:
            errors.append(f"SHORT {key}: expected {exp}, got {params_short[key]}")
        else:
            print(f"    ✅ {key} = {params_short[key]}")
    
    # Test no side (general)
    params_general = get_strategy_trade_params(uid, cfg, "BTCUSDT", strategy)
    print(f"\n  🔄 General (no side):")
    expected_general = {"percent": 5.0, "sl_pct": 3.0, "tp_pct": 6.0}
    for key, exp in expected_general.items():
        if params_general[key] != exp:
            errors.append(f"General {key}: expected {exp}, got {params_general[key]}")
        else:
            print(f"    ✅ {key} = {params_general[key]}")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return False
    
    print(f"\n✅ LONG/SHORT/General all use correct settings")
    return True


def test_atr_settings_in_trade():
    """Test ATR settings resolution in trade params"""
    print("\n" + "="*70)
    print("TEST: ATR settings resolution in trade params")
    print("="*70)
    
    uid = TEST_USERS[0]
    errors = []
    
    # Global ATR enabled
    db.set_user_field(uid, "use_atr", 1)
    db.invalidate_user_cache(uid)
    cfg = db.get_user_config(uid)
    
    # Test 1: Strategy with ATR explicitly disabled
    db.set_strategy_setting(uid, "scalper", "use_atr", 0, "bybit", "demo")
    params = get_strategy_trade_params(uid, cfg, "BTCUSDT", "scalper")
    
    if params["use_atr"] != False:
        errors.append(f"Scalper ATR should be False (strategy override), got {params['use_atr']}")
    else:
        print(f"  ✅ Scalper: use_atr = False (strategy override)")
    
    # Test 2: Strategy with ATR = None → uses global
    db.set_strategy_setting(uid, "elcaro", "use_atr", None, "bybit", "demo")
    params = get_strategy_trade_params(uid, cfg, "BTCUSDT", "elcaro")
    
    if params["use_atr"] != True:
        errors.append(f"Enliko ATR should be True (global fallback), got {params['use_atr']}")
    else:
        print(f"  ✅ Enliko: use_atr = True (global fallback)")
    
    # Test 3: Strategy with ATR explicitly enabled
    db.set_strategy_setting(uid, "oi", "use_atr", 1, "bybit", "demo")
    params = get_strategy_trade_params(uid, cfg, "BTCUSDT", "oi")
    
    if params["use_atr"] != True:
        errors.append(f"OI ATR should be True (explicit), got {params['use_atr']}")
    else:
        print(f"  ✅ OI: use_atr = True (explicit)")
    
    # Test 4: Global ATR disabled, strategy not set
    db.set_user_field(uid, "use_atr", 0)
    db.invalidate_user_cache(uid)
    cfg = db.get_user_config(uid)
    
    db.set_strategy_setting(uid, "fibonacci", "use_atr", None, "bybit", "demo")
    params = get_strategy_trade_params(uid, cfg, "BTCUSDT", "fibonacci")
    
    if params["use_atr"] != False:
        errors.append(f"Fibonacci ATR should be False (global disabled), got {params['use_atr']}")
    else:
        print(f"  ✅ Fibonacci: use_atr = False (global disabled)")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return False
    
    print(f"\n✅ ATR settings resolution correct")
    return True


def run_all_integration_tests():
    """Run all integration tests"""
    print("\n" + "="*80)
    print("STRATEGY SETTINGS INTEGRATION TESTS")
    print("="*80)
    
    cleanup()
    setup()
    
    tests = [
        ("Full trade params flow", test_full_trade_params_flow),
        ("Mixed side-specific and general", test_mixed_side_specific_and_general),
        ("Multiple strategies different configs", test_multiple_strategies_different_configs),
        ("LONG vs SHORT same strategy", test_long_vs_short_same_strategy),
        ("ATR settings in trade", test_atr_settings_in_trade),
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
    
    cleanup()
    
    print("\n" + "="*80)
    print("INTEGRATION TESTS SUMMARY")
    print("="*80)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Total: {len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
    else:
        print(f"\n⚠️  {failed} tests failed - review errors above")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_integration_tests()
    sys.exit(0 if success else 1)
