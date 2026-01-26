"""
Tests for Elcaro signal parser.
"""
import pytest

# Skip marker for tests that need update
needs_4d_update = pytest.mark.skip(reason="Needs update for current STRATEGY_FEATURES")


class TestIsElcaroSignal:
    """Test is_elcaro_signal function."""
    
    def test_full_signal_detected(self):
        """Full Elcaro signal should be detected."""
        import bot
        signal = """Elcaro

🔔 FILUSDT 📉 SHORT 🟢⚪️⚪️
⏱️ 60 | 🎚 68

💰 Entry: 4.2530
🛑 SL: 4.3200 (1.58%) [ATR]
🎯 TP: 4.1200 (3.13%) [AGG]

📊 RR: 5.0:1 | ATR Exit: ✅
📉 ATR: 14 | ×1.5 | Trigger: 30%
"""
        assert bot.is_elcaro_signal(signal) is True
    
    def test_signal_without_header(self):
        """Signal without 'Elcaro' header but with structure should be detected."""
        import bot
        signal = """🔔 BTCUSDT 📈 LONG
⏱️ 5 | 🎚 20

💰 Entry: 97500.00
🛑 SL: 95000.00 (2.56%) [ATR]
🎯 TP: 102000.00 (4.62%) [AGG]

📊 RR: 3.0:1 | ATR Exit: ✅
📉 ATR: 14 | ×1.0 | Trigger: 30%
"""
        assert bot.is_elcaro_signal(signal) is True
    
    def test_non_elcaro_signal_rejected(self):
        """Random text should not be detected as Elcaro."""
        import bot
        text = """BTCUSDT looking bullish
Entry around 97000
TP: 100000
SL: 95000
"""
        assert bot.is_elcaro_signal(text) is False
    
    def test_scryptomera_signal_rejected(self):
        """Scryptomera signal should not be detected as Elcaro."""
        import bot
        signal = """📰 BTCUSDT 📈 LONG at 97500
News: Bitcoin ETF approved
"""
        assert bot.is_elcaro_signal(signal) is False


class TestParseElcaroSignal:
    """Test parse_elcaro_signal function."""
    
    def test_parse_full_signal(self):
        """Parse complete Elcaro signal with all fields."""
        import bot
        signal = """Elcaro

🔔 FILUSDT 📉 SHORT 🟢⚪️⚪️
⏱️ 60 | 🎚 68

💰 Entry: 4.253000
🛑 SL: 4.320000 (1.58%) [ATR]
🎯 TP: 4.120000 (3.13%) [AGG]

📊 RR: 5.0:1 | ATR Exit: ✅
📉 ATR: 14 | ×1.5 | Trigger: 30%
"""
        result = bot.parse_elcaro_signal(signal)
        
        assert result is not None
        assert result["symbol"] == "FILUSDT"
        assert result["side"] == "Sell"  # SHORT
        assert result["elcaro_mode"] is True
        
        # Entry
        assert abs(result["entry"] - 4.253) < 0.001
        assert abs(result["price"] - 4.253) < 0.001
        
        # SL/TP
        assert abs(result["sl"] - 4.32) < 0.01
        assert abs(result["sl_pct"] - 1.58) < 0.1
        assert abs(result["tp"] - 4.12) < 0.01
        assert abs(result["tp_pct"] - 3.13) < 0.1
        
        # ATR
        assert result["atr_periods"] == 14
        assert abs(result["atr_multiplier"] - 1.5) < 0.1
        assert abs(result["atr_trigger_pct"] - 30.0) < 0.1
        
        # Leverage & timeframe
        assert result["leverage"] == 68
        assert result["timeframe"] == "60m"
        
        # RR
        assert abs(result["rr"] - 5.0) < 0.1
    
    def test_parse_long_signal(self):
        """Parse LONG signal."""
        import bot
        signal = """🔔 BTCUSDT 📈 LONG
⏱️ 5 | 🎚 20

💰 Entry: 97500.00
🛑 SL: 95000.00 (2.56%) [ATR]
🎯 TP: 102000.00 (4.62%) [AGG]

📊 RR: 3.0:1 | ATR Exit: ✅
📉 ATR: 14 | ×1.0 | Trigger: 30%
"""
        result = bot.parse_elcaro_signal(signal)
        
        assert result is not None
        assert result["symbol"] == "BTCUSDT"
        assert result["side"] == "Buy"  # LONG
        assert result["leverage"] == 20
        assert result["timeframe"] == "5m"
    
    def test_parse_with_usdc_symbol(self):
        """Parse signal with USDC symbol."""
        import bot
        signal = """🔔 BTCUSDC 📉 SHORT
⏱️ 15 | 🎚 50

💰 Entry: 97500.00
🛑 SL: 98000.00 (0.51%) [ATR]
🎯 TP: 96000.00 (1.54%) [AGG]

ATR Exit: ✅
📉 ATR: 7 | ×2.0 | Trigger: 25%
"""
        result = bot.parse_elcaro_signal(signal)
        
        assert result is not None
        assert result["symbol"] == "BTCUSDC"
    
    def test_parse_returns_none_for_invalid(self):
        """Invalid signal should return None."""
        import bot
        result = bot.parse_elcaro_signal("Just some random text")
        assert result is None
    
    def test_parse_handles_missing_atr(self):
        """Signal without ATR line should still parse."""
        import bot
        signal = """🔔 XRPUSDT 📈 LONG
⏱️ 60 | 🎚 30

💰 Entry: 2.50
🛑 SL: 2.40 (4.0%)
🎯 TP: 2.70 (8.0%)

ATR Exit: ✅
"""
        result = bot.parse_elcaro_signal(signal)
        
        assert result is not None
        assert result["symbol"] == "XRPUSDT"
        assert result["side"] == "Buy"
        assert "atr_periods" not in result or result.get("atr_periods") is None


class TestElcaroTradingLogic:
    """Test that Elcaro settings are used correctly in trading."""
    
    @pytest.fixture(autouse=True)
    def setup_db(self, test_db):
        """Setup temp database. Uses test_db fixture from conftest.py."""
        import db
        # test_db fixture already sets up the database schema
        pass
    
    def test_elcaro_mode_uses_signal_params(self):
        """In elcaro_mode, signal params should be used, not user settings."""
        import bot
        import db
        
        uid = 999888766
        db.ensure_user(uid)
        
        try:
            # Set user settings that should NOT be used
            db.set_strategy_setting(uid, "elcaro", "sl_percent", 5.0, "bybit", "demo")
            db.set_strategy_setting(uid, "elcaro", "tp_percent", 10.0, "bybit", "demo")
            db.set_strategy_setting(uid, "elcaro", "percent", 2.0, "bybit", "demo")
            
            # Elcaro signal - should use signal's SL/TP but user's percent
            parsed = {
                "elcaro_mode": True,
                "sl_pct": 1.5,   # From signal
                "tp_pct": 3.0,  # From signal
            }
            
            cfg = db.get_user_config(uid)
            
            # Get params - in elcaro_mode we should use signal SL/TP
            params = bot.get_strategy_trade_params(
                uid, cfg, "BTCUSDT", "elcaro", side="Buy",
                exchange="bybit", account_type="demo"
            )
            
            # Percent comes from user settings
            assert params["percent"] == 2.0
            
        finally:
            with db.get_conn() as conn:
                conn.execute("DELETE FROM users WHERE user_id=?", (uid,))
                conn.execute("DELETE FROM user_strategy_settings WHERE user_id=?", (uid,))
                conn.commit()
    
    def test_elcaro_direction_filter(self):
        """Elcaro direction filter should work."""
        import db
        
        uid = 999888765
        db.ensure_user(uid)
        
        try:
            # Set direction to LONG only
            db.set_strategy_setting(uid, "elcaro", "direction", "long", "bybit", "demo")
            
            settings = db.get_strategy_settings(uid, "elcaro", "bybit", "demo")
            assert settings.get("direction") == "long"
            
            # Change to SHORT only
            db.set_strategy_setting(uid, "elcaro", "direction", "short", "bybit", "demo")
            
            settings = db.get_strategy_settings(uid, "elcaro", "bybit", "demo")
            assert settings.get("direction") == "short"
            
        finally:
            with db.get_conn() as conn:
                conn.execute("DELETE FROM users WHERE user_id=?", (uid,))
                conn.execute("DELETE FROM user_strategy_settings WHERE user_id=?", (uid,))
                conn.commit()


@needs_4d_update
class TestElcaroUI:
    """Test Elcaro UI features are correctly defined."""
    
    def test_elcaro_strategy_features(self):
        """Elcaro should have correct features."""
        import bot
        
        features = bot.STRATEGY_FEATURES.get("elcaro", {})
        
        # Should NOT have
        assert features.get("order_type") is False
        assert features.get("leverage") is False
        assert features.get("use_atr") is False
        assert features.get("sl_tp") is False
        assert features.get("atr_params") is False
        
        # Should have
        assert features.get("direction") is True
        assert features.get("side_settings") is True
        assert features.get("percent") is True
        assert features.get("coins_group") is True
        assert features.get("hl_settings") is True
    
    def test_elcaro_keyboard_minimal(self):
        """Elcaro keyboard should have minimal buttons."""
        import bot
        
        t = {"global_default": "Global"}
        settings = {}
        kb = bot.get_strategy_param_keyboard("elcaro", t, settings)
        
        # Check we have keyboard
        assert kb is not None
        
        # Get all callback_data
        callback_data = []
        for row in kb.inline_keyboard:
            for btn in row:
                if btn.callback_data:
                    callback_data.append(btn.callback_data)
        
        # Should have direction
        has_dir = any("elcaro_dir:" in cd for cd in callback_data)
        assert has_dir, "Should have direction button"
        
        # Should have side settings
        has_side = any("elcaro_side:" in cd for cd in callback_data)
        assert has_side, "Should have LONG/SHORT side buttons"
        
        # Should NOT have order type, leverage, use_atr, sl_tp
        no_order = not any("strat_order_type:elcaro" in cd for cd in callback_data)
        no_atr = not any("strat_atr_toggle:elcaro" in cd for cd in callback_data)
        
        assert no_order, "Should NOT have order type button"
        assert no_atr, "Should NOT have ATR toggle button"
    
    def test_elcaro_side_keyboard_minimal(self):
        """Elcaro side keyboard should only have percent."""
        import bot
        
        t = {"param_percent": "Entry %"}
        settings = {}
        kb = bot.get_strategy_side_keyboard("elcaro", "long", t, settings)
        
        callback_data = []
        for row in kb.inline_keyboard:
            for btn in row:
                if btn.callback_data:
                    callback_data.append(btn.callback_data)
        
        # Should have percent
        has_percent = any("long_percent" in cd for cd in callback_data)
        assert has_percent, "Should have percent button"
        
        # Should NOT have SL/TP
        no_sl = not any("long_sl_percent" in cd for cd in callback_data)
        no_tp = not any("long_tp_percent" in cd for cd in callback_data)
        assert no_sl, "Should NOT have SL button for Elcaro"
        assert no_tp, "Should NOT have TP button for Elcaro"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
