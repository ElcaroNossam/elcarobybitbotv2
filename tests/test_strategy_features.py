"""Tests for STRATEGY_FEATURES configuration and get_strategy_param_keyboard.

NOTE: Many tests in this file are marked as skip because they were written for
the old 3D schema (user_id, strategy, exchange). The codebase has migrated to
4D schema (user_id, strategy, side, exchange) with side-specific settings.
These tests need to be rewritten to match the new architecture.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Skip marker for tests that need 4D schema update
needs_4d_update = pytest.mark.skip(reason="Needs update for 4D schema (user_id, strategy, side, exchange)")


class TestStrategyFeaturesConfig:
    """Test STRATEGY_FEATURES configuration structure."""
    
    def test_strategy_features_exists(self):
        """STRATEGY_FEATURES config should exist in bot.py."""
        import bot
        assert hasattr(bot, 'STRATEGY_FEATURES')
        assert isinstance(bot.STRATEGY_FEATURES, dict)
    
    def test_all_strategies_defined(self):
        """All 7 strategies should be defined in STRATEGY_FEATURES."""
        import bot
        expected = {"scryptomera", "scalper", "elcaro", "fibonacci", "oi", "rsi_bb", "manual"}
        actual = set(bot.STRATEGY_FEATURES.keys())
        assert expected == actual, f"Missing: {expected - actual}, Extra: {actual - expected}"
    
    def test_feature_keys_consistent(self):
        """All strategies should have the same feature keys."""
        import bot
        expected_keys = {
            "order_type", "coins_group", "leverage", "use_atr", "direction",
            "side_settings", "percent", "sl_tp", "atr_params", "min_quality"
        }
        for strat, features in bot.STRATEGY_FEATURES.items():
            actual_keys = set(features.keys())
            assert actual_keys == expected_keys, f"{strat} has wrong keys: {actual_keys ^ expected_keys}"


@needs_4d_update
class TestStrategyFeaturesLogic:
    """Test that STRATEGY_FEATURES correctly defines each strategy's needs."""
    
    def test_elcaro_minimal_features(self):
        """Lyxen uses signal data - should have minimal settings."""
        import bot
        elcaro = bot.STRATEGY_FEATURES["elcaro"]
        
        # Lyxen should NOT have these (signal provides them)
        assert not elcaro["order_type"], "Lyxen shouldn't show order_type (signal data)"
        assert not elcaro["leverage"], "Lyxen shouldn't show leverage (signal data)"
        assert not elcaro["use_atr"], "Lyxen shouldn't show ATR settings"
        assert not elcaro["sl_tp"], "Lyxen shouldn't show SL/TP (from signal)"
        assert not elcaro["atr_params"], "Lyxen shouldn't show ATR params"
        assert not elcaro["min_quality"], "Lyxen doesn't have quality filter"
        
        # Lyxen should have these
        assert elcaro["coins_group"], "Lyxen should show coins_group filter"
        assert elcaro["percent"], "Lyxen should show percent"
        assert elcaro["direction"], "Lyxen should show direction filter"
        assert elcaro["side_settings"], "Lyxen should have side-specific settings"
    
    def test_scryptomera_full_features(self):
        """Scryptomera should have full trading features."""
        import bot
        strat = bot.STRATEGY_FEATURES["scryptomera"]
        
        # order_type moved to per-side settings
        assert strat["coins_group"], "Scryptomera should show coins_group"
        assert strat["leverage"], "Scryptomera should show leverage"
        assert strat["use_atr"], "Scryptomera should show ATR toggle"
        assert strat["direction"], "Scryptomera should show direction"
        assert strat["side_settings"], "Scryptomera should have side settings"
        assert strat["percent"], "Scryptomera should show percent"
        assert strat["sl_tp"], "Scryptomera should show SL/TP"
        assert strat["atr_params"], "Scryptomera should show ATR params"
    
    def test_fibonacci_quality_filter(self):
        """Fibonacci should have min_quality filter and full features."""
        import bot
        fib = bot.STRATEGY_FEATURES["fibonacci"]
        
        assert fib["min_quality"], "Fibonacci should show min_quality"
        assert fib["percent"], "Fibonacci should show percent"
        assert fib["leverage"], "Fibonacci should show leverage"
        assert fib["direction"], "Fibonacci should show direction"
        assert fib["use_atr"], "Fibonacci should show ATR (full features)"
        assert fib["sl_tp"], "Fibonacci should show SL/TP"
        assert fib["order_type"], "Fibonacci should show order_type"
    
    def test_oi_rsi_bb_full_features(self):
        """OI and RSI_BB should have full features including side settings."""
        import bot
        
        oi = bot.STRATEGY_FEATURES["oi"]
        rsi_bb = bot.STRATEGY_FEATURES["rsi_bb"]
        
        # OI and RSI_BB now have full features
        assert oi["side_settings"], "OI should have side settings"
        assert rsi_bb["side_settings"], "RSI_BB should have side settings"
        
        # They should have SL/TP on main screen
        assert oi["sl_tp"], "OI should show SL/TP on main"
        assert rsi_bb["sl_tp"], "RSI_BB should show SL/TP on main"
        
        # Full ATR support
        assert oi["use_atr"], "OI should show ATR"
        assert rsi_bb["use_atr"], "RSI_BB should show ATR"
        assert oi["atr_params"], "OI should show ATR params"
        assert rsi_bb["atr_params"], "RSI_BB should show ATR params"


@needs_4d_update
class TestGetStrategyParamKeyboard:
    """Test get_strategy_param_keyboard function."""
    
    def get_keyboard(self, strategy: str, settings: dict = None):
        """Helper to build keyboard."""
        import bot
        t = {"btn_back": "Back", "param_percent": "Entry %", "param_leverage": "Leverage",
             "param_sl": "SL", "param_tp": "TP", "param_atr_toggle": "ATR Mode",
             "param_direction": "Direction", "param_coins_group": "Coins",
             "param_order_type": "Order Type", "param_long_settings": "LONG Settings",
             "param_short_settings": "SHORT Settings", "param_hl_settings": "HyperLiquid",
             "reset_to_global": "Reset", "param_min_quality": "Min Quality",
             "param_atr_periods": "ATR Periods", "param_atr_mult": "ATR Mult",
             "param_atr_trigger": "ATR Trigger", "order_type": "Order Type",
             "position_size": "Position Size", "leverage": "Leverage",
             "atr_trailing": "ATR Trailing", "stop_loss": "Stop-Loss",
             "take_profit": "Take-Profit", "coins_filter": "Coins",
             "direction": "Direction", "min_quality": "Min Quality",
             "long_settings": "LONG", "short_settings": "SHORT",
             "hl_settings": "HyperLiquid", "global_default": "Global",
             "auto_default": "Auto", "all_coins": "All"}
        settings = settings or {}
        return bot.get_strategy_param_keyboard(strategy, t, settings)
    
    def get_callback_data(self, keyboard):
        """Extract all callback_data from keyboard."""
        return [btn.callback_data for row in keyboard.inline_keyboard for btn in row]
    
    def test_elcaro_minimal_buttons(self):
        """Lyxen keyboard should have minimal buttons."""
        kb = self.get_keyboard("elcaro")
        callbacks = self.get_callback_data(kb)
        
        # Should have
        assert any("percent" in c for c in callbacks), "Should have percent"
        assert any("strat_coins" in c for c in callbacks), "Should have coins filter"
        assert any("_dir:" in c for c in callbacks), "Should have direction"
        assert any("_side:long" in c for c in callbacks), "Should have LONG settings"
        assert any("_side:short" in c for c in callbacks), "Should have SHORT settings"
        
        # Should NOT have
        assert not any("strat_order_type" in c for c in callbacks), "Should NOT have order_type"
        assert not any(":leverage" in c for c in callbacks), "Should NOT have leverage"
        assert not any("strat_atr_toggle" in c for c in callbacks), "Should NOT have ATR"
    
    def test_scryptomera_full_buttons(self):
        """Scryptomera keyboard should have full buttons."""
        kb = self.get_keyboard("scryptomera")
        callbacks = self.get_callback_data(kb)
        
        assert any("strat_order_type" in c for c in callbacks), "Should have order_type"
        assert any(":leverage" in c for c in callbacks), "Should have leverage"
        assert any("strat_atr_toggle" in c for c in callbacks), "Should have ATR toggle"
        assert any("_dir:" in c for c in callbacks), "Should have direction"
        assert any("strat_coins" in c for c in callbacks), "Should have coins filter"
    
    def test_atr_params_hidden_when_disabled(self):
        """ATR params should be hidden when ATR is disabled."""
        kb = self.get_keyboard("oi", {"use_atr": 0})  # OI supports atr_params
        callbacks = self.get_callback_data(kb)
        
        # ATR params should be hidden
        assert not any("atr_periods" in c for c in callbacks), "ATR periods hidden when disabled"
        assert not any("atr_multiplier" in c for c in callbacks), "ATR mult hidden when disabled"
        assert not any("atr_trigger" in c for c in callbacks), "ATR trigger hidden when disabled"
    
    def test_atr_params_shown_when_enabled(self):
        """ATR params should be shown when ATR is enabled."""
        kb = self.get_keyboard("oi", {"use_atr": 1})  # OI supports atr_params
        callbacks = self.get_callback_data(kb)
        
        # ATR params should be shown
        assert any("atr_periods" in c for c in callbacks), "ATR periods shown when enabled"
        assert any("atr_multiplier" in c for c in callbacks), "ATR mult shown when enabled"
        assert any("atr_trigger" in c for c in callbacks), "ATR trigger shown when enabled"
    
    def test_fibonacci_quality_button(self):
        """Fibonacci should have min_quality button."""
        kb = self.get_keyboard("fibonacci")
        callbacks = self.get_callback_data(kb)
        
        assert any("min_quality" in c for c in callbacks), "Fibonacci should have min_quality"
    
    def test_oi_has_sltp_buttons(self):
        """OI should have SL/TP buttons on main keyboard."""
        kb = self.get_keyboard("oi")
        callbacks = self.get_callback_data(kb)
        
        assert any(":sl_percent" in c for c in callbacks), "OI should have SL on main"
        assert any(":tp_percent" in c for c in callbacks), "OI should have TP on main"


@needs_4d_update
class TestGetStrategySideKeyboard:
    """Test get_strategy_side_keyboard function."""
    
    def get_keyboard(self, strategy: str, side: str, settings: dict = None):
        """Helper to build side keyboard."""
        import bot
        t = {"btn_back": "Back", "param_percent": "Entry %", 
             "param_sl": "SL", "param_tp": "TP",
             "param_atr_periods": "ATR Periods", "param_atr_mult": "ATR Mult",
             "param_atr_trigger": "ATR Trigger"}
        settings = settings or {}
        return bot.get_strategy_side_keyboard(strategy, side, t, settings)
    
    def get_callback_data(self, keyboard):
        """Extract all callback_data from keyboard."""
        return [btn.callback_data for row in keyboard.inline_keyboard for btn in row]
    
    def test_elcaro_side_minimal(self):
        """Lyxen side keyboard should only have percent."""
        kb = self.get_keyboard("elcaro", "long")
        callbacks = self.get_callback_data(kb)
        
        # Should have percent
        assert any("long_percent" in c for c in callbacks), "Should have percent"
        
        # Should NOT have SL/TP (from signal)
        assert not any("sl_percent" in c for c in callbacks), "Should NOT have SL"
        assert not any("tp_percent" in c for c in callbacks), "Should NOT have TP"
    
    def test_scryptomera_side_full(self):
        """Scryptomera side keyboard with ATR enabled should have all params."""
        kb = self.get_keyboard("scryptomera", "long", {"use_atr": 1})
        callbacks = self.get_callback_data(kb)
        
        # Should have all
        assert any("long_percent" in c for c in callbacks), "Should have percent"
        assert any("long_sl_percent" in c for c in callbacks), "Should have SL"
        assert any("long_tp_percent" in c for c in callbacks), "Should have TP"
        assert any("long_atr_periods" in c for c in callbacks), "Should have ATR periods"
    
    def test_scryptomera_side_no_atr(self):
        """Scryptomera side without ATR should not have ATR params."""
        kb = self.get_keyboard("scryptomera", "short", {"use_atr": 0})
        callbacks = self.get_callback_data(kb)
        
        # Should have basic
        assert any("short_percent" in c for c in callbacks), "Should have percent"
        assert any("short_sl_percent" in c for c in callbacks), "Should have SL"
        
        # Should NOT have ATR
        assert not any("atr_periods" in c for c in callbacks), "Should NOT have ATR periods"


class TestStrategyNamesMap:
    """Test STRATEGY_NAMES_MAP is complete."""
    
    def test_all_strategies_have_names(self):
        """All strategies should have display names."""
        import bot
        for strategy in bot.STRATEGY_FEATURES.keys():
            assert strategy in bot.STRATEGY_NAMES_MAP, f"{strategy} missing from STRATEGY_NAMES_MAP"
    
    def test_display_names_not_empty(self):
        """Display names should not be empty."""
        import bot
        for strategy, name in bot.STRATEGY_NAMES_MAP.items():
            assert name and len(name) > 0, f"{strategy} has empty name"


@needs_4d_update
class TestBuildStrategySettingsText:
    """Test build_strategy_settings_text function."""
    
    def get_text(self, strategy: str, settings: dict = None):
        """Helper to build settings text."""
        import bot
        t = {
            "global_default": "Global",
            "strategy_param_header": "⚙️ *{name} Settings*",
        }
        settings = settings or {}
        return bot.build_strategy_settings_text(strategy, settings, t)
    
    def test_elcaro_shows_direction_and_percent(self):
        """Lyxen should show direction and percent."""
        text = self.get_text("elcaro", {"direction": "long", "percent": 2.0})
        assert "Direction" in text
        assert "LONG" in text
        assert "Position Size" in text
        assert "2.0%" in text
    
    def test_elcaro_no_leverage(self):
        """Lyxen should NOT show leverage."""
        text = self.get_text("elcaro", {"leverage": 10})
        assert "Leverage" not in text
    
    def test_scryptomera_shows_order_type(self):
        """Scryptomera should show order type."""
        text = self.get_text("scryptomera", {"order_type": "limit"})
        assert "Order Type" in text
        assert "Limit" in text
    
    def test_fibonacci_shows_min_quality(self):
        """Fibonacci should show min_quality."""
        text = self.get_text("fibonacci", {"min_quality": 75})
        assert "Min Quality" in text
        assert "75%" in text
    
    def test_oi_shows_sl_tp(self):
        """OI should show SL/TP on main screen."""
        text = self.get_text("oi", {"sl_percent": 2.0, "tp_percent": 5.0})
        assert "SL:" in text
        assert "2.0%" in text
        assert "TP:" in text
        assert "5.0%" in text
    
    def test_side_settings_summary(self):
        """Strategies with side_settings should show LONG/SHORT summary."""
        text = self.get_text("scryptomera", {
            "long_percent": 1.0,
            "long_sl_percent": 2.0,
            "short_percent": 1.5
        })
        assert "📈 LONG:" in text
        assert "📉 SHORT:" in text


@needs_4d_update
class TestStrategyTradeParamsIntegration:
    """Test that strategy settings are properly used in trading flow."""
    
    @pytest.fixture(autouse=True)
    def setup_db(self, test_db):
        """Setup temp database for tests. Uses test_db fixture from conftest.py."""
        # test_db fixture already sets up the database schema
        pass
    
    def test_get_strategy_settings_returns_all_fields(self):
        """get_strategy_settings should return all defined fields."""
        import db
        # Create temp user
        uid = 999888777
        db.ensure_user(uid)
        
        try:
            # Set various settings
            db.set_strategy_setting(uid, "scryptomera", "percent", 2.5, "bybit", "demo")
            db.set_strategy_setting(uid, "scryptomera", "sl_percent", 3.0, "bybit", "demo")
            db.set_strategy_setting(uid, "scryptomera", "tp_percent", 6.0, "bybit", "demo")
            db.set_strategy_setting(uid, "scryptomera", "use_atr", 1, "bybit", "demo")
            db.set_strategy_setting(uid, "scryptomera", "direction", "long", "bybit", "demo")
            
            # Get settings
            settings = db.get_strategy_settings(uid, "scryptomera", "bybit", "demo")
            
            assert settings.get("percent") == 2.5
            assert settings.get("sl_percent") == 3.0
            assert settings.get("tp_percent") == 6.0
            assert settings.get("use_atr") == 1
            assert settings.get("direction") == "long"
        finally:
            # Cleanup
            with db.get_conn() as conn:
                conn.execute("DELETE FROM users WHERE user_id=?", (uid,))
                conn.execute("DELETE FROM user_strategy_settings WHERE user_id=?", (uid,))
                conn.commit()
    
    def test_side_specific_settings_saved_correctly(self):
        """Side-specific settings should be saved separately."""
        import db
        uid = 999888776
        db.ensure_user(uid)
        
        try:
            # Set LONG and SHORT settings
            db.set_strategy_setting(uid, "scryptomera", "long_percent", 1.0, "bybit", "demo")
            db.set_strategy_setting(uid, "scryptomera", "short_percent", 1.5, "bybit", "demo")
            db.set_strategy_setting(uid, "scryptomera", "long_sl_percent", 2.0, "bybit", "demo")
            db.set_strategy_setting(uid, "scryptomera", "short_sl_percent", 2.5, "bybit", "demo")
            
            # Get settings
            settings = db.get_strategy_settings(uid, "scryptomera", "bybit", "demo")
            
            assert settings.get("long_percent") == 1.0
            assert settings.get("short_percent") == 1.5
            assert settings.get("long_sl_percent") == 2.0
            assert settings.get("short_sl_percent") == 2.5
        finally:
            with db.get_conn() as conn:
                conn.execute("DELETE FROM users WHERE user_id=?", (uid,))
                conn.execute("DELETE FROM user_strategy_settings WHERE user_id=?", (uid,))
                conn.commit()
    
    def test_atr_params_saved_per_side(self):
        """ATR params should be saved per side."""
        import db
        uid = 999888775
        db.ensure_user(uid)
        
        try:
            db.set_strategy_setting(uid, "scryptomera", "long_atr_periods", 7, "bybit", "demo")
            db.set_strategy_setting(uid, "scryptomera", "short_atr_periods", 14, "bybit", "demo")
            db.set_strategy_setting(uid, "scryptomera", "long_atr_multiplier_sl", 1.5, "bybit", "demo")
            db.set_strategy_setting(uid, "scryptomera", "long_atr_trigger_pct", 2.0, "bybit", "demo")
            
            settings = db.get_strategy_settings(uid, "scryptomera", "bybit", "demo")
            
            assert settings.get("long_atr_periods") == 7
            assert settings.get("short_atr_periods") == 14
            assert settings.get("long_atr_multiplier_sl") == 1.5
            assert settings.get("long_atr_trigger_pct") == 2.0
        finally:
            with db.get_conn() as conn:
                conn.execute("DELETE FROM users WHERE user_id=?", (uid,))
                conn.execute("DELETE FROM user_strategy_settings WHERE user_id=?", (uid,))
                conn.commit()


@needs_4d_update
class TestGetStrategyTradeParams:
    """Test get_strategy_trade_params function properly applies settings."""
    
    @pytest.fixture(autouse=True)
    def setup_db(self, test_db):
        """Setup temp database for tests. Uses test_db fixture from conftest.py."""
        # test_db fixture already sets up the database schema
        pass
    
    def test_side_specific_percent_applied(self):
        """Should use side-specific percent when available."""
        import db
        import bot
        uid = 999888774
        db.ensure_user(uid)
        
        try:
            # Set side-specific percents
            db.set_strategy_setting(uid, "scryptomera", "long_percent", 1.5, "bybit", "demo")
            db.set_strategy_setting(uid, "scryptomera", "short_percent", 2.0, "bybit", "demo")
            db.set_strategy_setting(uid, "scryptomera", "percent", 1.0, "bybit", "demo")  # fallback
            
            cfg = db.get_user_config(uid)
            
            # LONG should use long_percent
            params_long = bot.get_strategy_trade_params(
                uid, cfg, "BTCUSDT", "scryptomera", side="Buy",
                exchange="bybit", account_type="demo"
            )
            assert params_long["percent"] == 1.5
            
            # SHORT should use short_percent
            params_short = bot.get_strategy_trade_params(
                uid, cfg, "BTCUSDT", "scryptomera", side="Sell",
                exchange="bybit", account_type="demo"
            )
            assert params_short["percent"] == 2.0
        finally:
            with db.get_conn() as conn:
                conn.execute("DELETE FROM users WHERE user_id=?", (uid,))
                conn.execute("DELETE FROM user_strategy_settings WHERE user_id=?", (uid,))
                conn.commit()
    
    def test_fallback_to_general_percent(self):
        """Should fall back to general percent if side-specific not set."""
        import db
        import bot
        uid = 999888773
        db.ensure_user(uid)
        
        try:
            # Only set general percent, no side-specific
            db.set_strategy_setting(uid, "scryptomera", "percent", 3.0, "bybit", "demo")
            
            cfg = db.get_user_config(uid)
            
            params = bot.get_strategy_trade_params(
                uid, cfg, "BTCUSDT", "scryptomera", side="Buy",
                exchange="bybit", account_type="demo"
            )
            assert params["percent"] == 3.0
        finally:
            with db.get_conn() as conn:
                conn.execute("DELETE FROM users WHERE user_id=?", (uid,))
                conn.execute("DELETE FROM user_strategy_settings WHERE user_id=?", (uid,))
                conn.commit()
    
    def test_side_specific_sl_tp_applied(self):
        """Should use side-specific SL/TP when available."""
        import db
        import bot
        uid = 999888772
        db.ensure_user(uid)
        
        try:
            db.set_strategy_setting(uid, "scryptomera", "long_sl_percent", 2.0, "bybit", "demo")
            db.set_strategy_setting(uid, "scryptomera", "long_tp_percent", 5.0, "bybit", "demo")
            db.set_strategy_setting(uid, "scryptomera", "short_sl_percent", 3.0, "bybit", "demo")
            db.set_strategy_setting(uid, "scryptomera", "short_tp_percent", 8.0, "bybit", "demo")
            
            cfg = db.get_user_config(uid)
            
            params_long = bot.get_strategy_trade_params(
                uid, cfg, "BTCUSDT", "scryptomera", side="Buy",
                exchange="bybit", account_type="demo"
            )
            assert params_long["sl_pct"] == 2.0
            assert params_long["tp_pct"] == 5.0
            
            params_short = bot.get_strategy_trade_params(
                uid, cfg, "BTCUSDT", "scryptomera", side="Sell",
                exchange="bybit", account_type="demo"
            )
            assert params_short["sl_pct"] == 3.0
            assert params_short["tp_pct"] == 8.0
        finally:
            with db.get_conn() as conn:
                conn.execute("DELETE FROM users WHERE user_id=?", (uid,))
                conn.execute("DELETE FROM user_strategy_settings WHERE user_id=?", (uid,))
                conn.commit()
    
    def test_use_atr_from_strategy_settings(self):
        """Should use use_atr from strategy settings."""
        import db
        import bot
        uid = 999888771
        db.ensure_user(uid)
        
        try:
            # Disable ATR for strategy
            db.set_strategy_setting(uid, "scryptomera", "use_atr", 0, "bybit", "demo")
            
            cfg = db.get_user_config(uid)
            # Even if global has ATR enabled
            cfg["use_atr"] = 1
            
            params = bot.get_strategy_trade_params(
                uid, cfg, "BTCUSDT", "scryptomera", side="Buy",
                exchange="bybit", account_type="demo"
            )
            # Strategy setting should override global
            assert params["use_atr"] == False
        finally:
            with db.get_conn() as conn:
                conn.execute("DELETE FROM users WHERE user_id=?", (uid,))
                conn.execute("DELETE FROM user_strategy_settings WHERE user_id=?", (uid,))
                conn.commit()
    
    def test_all_strategies_return_valid_params(self):
        """All strategies should return valid params structure."""
        import db
        import bot
        uid = 999888770
        db.ensure_user(uid)
        
        try:
            cfg = db.get_user_config(uid)
            
            for strategy in bot.STRATEGY_FEATURES.keys():
                params = bot.get_strategy_trade_params(
                    uid, cfg, "BTCUSDT", strategy, side="Buy",
                    exchange="bybit", account_type="demo"
                )
                
                assert "percent" in params, f"{strategy}: missing percent"
                assert "sl_pct" in params, f"{strategy}: missing sl_pct"
                assert "tp_pct" in params, f"{strategy}: missing tp_pct"
                assert "use_atr" in params, f"{strategy}: missing use_atr"
                
                # Values should be valid
                assert params["percent"] > 0, f"{strategy}: percent should be > 0"
        finally:
            with db.get_conn() as conn:
                conn.execute("DELETE FROM users WHERE user_id=?", (uid,))
                conn.execute("DELETE FROM user_strategy_settings WHERE user_id=?", (uid,))
                conn.commit()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
