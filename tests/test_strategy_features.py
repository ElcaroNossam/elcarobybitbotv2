"""Tests for STRATEGY_FEATURES configuration and get_strategy_param_keyboard."""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestStrategyFeaturesConfig:
    """Test STRATEGY_FEATURES configuration structure."""
    
    def test_strategy_features_exists(self):
        """STRATEGY_FEATURES config should exist in bot.py."""
        import bot
        assert hasattr(bot, 'STRATEGY_FEATURES')
        assert isinstance(bot.STRATEGY_FEATURES, dict)
    
    def test_all_strategies_defined(self):
        """All 6 strategies should be defined in STRATEGY_FEATURES."""
        import bot
        expected = {"scryptomera", "scalper", "elcaro", "fibonacci", "oi", "rsi_bb"}
        actual = set(bot.STRATEGY_FEATURES.keys())
        assert expected == actual, f"Missing: {expected - actual}, Extra: {actual - expected}"
    
    def test_feature_keys_consistent(self):
        """All strategies should have the same feature keys."""
        import bot
        expected_keys = {
            "order_type", "coins_group", "leverage", "use_atr", "direction",
            "side_settings", "percent", "sl_tp", "atr_params", "hl_settings", "min_quality"
        }
        for strat, features in bot.STRATEGY_FEATURES.items():
            actual_keys = set(features.keys())
            assert actual_keys == expected_keys, f"{strat} has wrong keys: {actual_keys ^ expected_keys}"


class TestStrategyFeaturesLogic:
    """Test that STRATEGY_FEATURES correctly defines each strategy's needs."""
    
    def test_elcaro_minimal_features(self):
        """Elcaro uses signal data - should have minimal settings."""
        import bot
        elcaro = bot.STRATEGY_FEATURES["elcaro"]
        
        # Elcaro should NOT have these (signal provides them)
        assert not elcaro["order_type"], "Elcaro shouldn't show order_type (signal data)"
        assert not elcaro["leverage"], "Elcaro shouldn't show leverage (signal data)"
        assert not elcaro["use_atr"], "Elcaro shouldn't show ATR settings"
        assert not elcaro["sl_tp"], "Elcaro shouldn't show SL/TP (from signal)"
        assert not elcaro["atr_params"], "Elcaro shouldn't show ATR params"
        assert not elcaro["min_quality"], "Elcaro doesn't have quality filter"
        
        # Elcaro should have these
        assert elcaro["coins_group"], "Elcaro should show coins_group filter"
        assert elcaro["percent"], "Elcaro should show percent"
        assert elcaro["direction"], "Elcaro should show direction filter"
        assert elcaro["side_settings"], "Elcaro should have side-specific settings"
    
    def test_scryptomera_full_features(self):
        """Scryptomera should have full trading features."""
        import bot
        strat = bot.STRATEGY_FEATURES["scryptomera"]
        
        assert strat["order_type"], "Scryptomera should show order_type"
        assert strat["coins_group"], "Scryptomera should show coins_group"
        assert strat["leverage"], "Scryptomera should show leverage"
        assert strat["use_atr"], "Scryptomera should show ATR toggle"
        assert strat["direction"], "Scryptomera should show direction"
        assert strat["side_settings"], "Scryptomera should have side settings"
        assert strat["hl_settings"], "Scryptomera should show HL settings"
    
    def test_fibonacci_quality_filter(self):
        """Fibonacci should have min_quality filter."""
        import bot
        fib = bot.STRATEGY_FEATURES["fibonacci"]
        
        assert fib["min_quality"], "Fibonacci should show min_quality"
        assert fib["percent"], "Fibonacci should show percent"
        assert fib["leverage"], "Fibonacci should show leverage"
        assert fib["direction"], "Fibonacci should show direction"
        assert not fib["use_atr"], "Fibonacci shouldn't show ATR"
    
    def test_oi_rsi_bb_no_side_settings(self):
        """OI and RSI_BB use global settings, no side-specific."""
        import bot
        
        oi = bot.STRATEGY_FEATURES["oi"]
        rsi_bb = bot.STRATEGY_FEATURES["rsi_bb"]
        
        # OI and RSI_BB don't need side-specific settings
        assert not oi["side_settings"], "OI shouldn't have side settings"
        assert not rsi_bb["side_settings"], "RSI_BB shouldn't have side settings"
        
        # But they should have SL/TP on main screen
        assert oi["sl_tp"], "OI should show SL/TP on main"
        assert rsi_bb["sl_tp"], "RSI_BB should show SL/TP on main"


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
        """Elcaro keyboard should have minimal buttons."""
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
        """Elcaro side keyboard should only have percent."""
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
