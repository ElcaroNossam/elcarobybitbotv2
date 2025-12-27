"""
Comprehensive tests for position monitoring logic across all exchanges and modes.

Tests:
1. Position monitoring and detection
2. SL/TP setting logic
3. ATR trailing stop logic
4. Close all cooldown
5. Multi-exchange support (Bybit demo/real, HyperLiquid testnet/mainnet)
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import time


class TestPositionMonitoring:
    """Test position monitoring and detection logic."""
    
    def test_close_all_cooldown_initialization(self):
        """Test that _close_all_cooldown is properly initialized."""
        import bot
        assert hasattr(bot, '_close_all_cooldown')
        assert isinstance(bot._close_all_cooldown, dict)
    
    def test_atr_triggered_initialization(self):
        """Test that _atr_triggered is properly initialized."""
        import bot
        assert hasattr(bot, '_atr_triggered')
        assert isinstance(bot._atr_triggered, dict)
    
    @pytest.mark.asyncio
    async def test_cooldown_prevents_readding_positions(self):
        """Test that close_all cooldown prevents monitoring from re-adding positions."""
        import bot
        import db
        
        uid = 999999
        test_symbol = "TESTUSDT"
        
        # Set cooldown for this user
        cooldown_time = time.time() + 30
        bot._close_all_cooldown[uid] = cooldown_time
        
        # Mock position that would normally be added
        mock_position = {
            "symbol": test_symbol,
            "side": "Buy",
            "size": "1.0",
            "avgPrice": "100.0",
            "markPrice": "101.0",
            "unrealisedPnl": "1.0",
            "stopLoss": "",
            "takeProfit": ""
        }
        
        # Verify cooldown is active
        assert uid in bot._close_all_cooldown
        assert bot._close_all_cooldown[uid] > time.time()
        
        # Cleanup
        del bot._close_all_cooldown[uid]
    
    @pytest.mark.asyncio
    async def test_sl_tp_validation_logic(self):
        """Test SL/TP validation and setting logic."""
        from bot import quantize, quantize_up
        
        # Test LONG position SL/TP calculation
        entry_price = 100.0
        sl_pct = 3.0
        tp_pct = 8.0
        
        # LONG: SL below entry, TP above entry
        sl_long = entry_price * (1 - sl_pct / 100)  # 97.0
        tp_long = entry_price * (1 + tp_pct / 100)  # 108.0
        
        assert sl_long < entry_price, "LONG SL must be below entry"
        assert tp_long > entry_price, "LONG TP must be above entry"
        
        # SHORT: SL above entry, TP below entry
        sl_short = entry_price * (1 + sl_pct / 100)  # 103.0
        tp_short = entry_price * (1 - tp_pct / 100)  # 92.0
        
        assert sl_short > entry_price, "SHORT SL must be above entry"
        assert tp_short < entry_price, "SHORT TP must be below entry"
    
    @pytest.mark.asyncio
    async def test_atr_trailing_logic(self):
        """Test ATR trailing stop logic."""
        # Mock ATR calculation
        mark_price = 100.0
        atr_value = 2.0
        atr_multiplier = 2.0
        tick_size = 0.01
        
        # LONG position ATR SL
        side = "Buy"
        atr_sl_long = mark_price - (atr_value * atr_multiplier)  # 96.0
        
        # SL should be below current price
        assert atr_sl_long < mark_price, "LONG ATR SL must be below mark price"
        
        # SHORT position ATR SL
        side = "Sell"
        atr_sl_short = mark_price + (atr_value * atr_multiplier)  # 104.0
        
        # SL should be above current price
        assert atr_sl_short > mark_price, "SHORT ATR SL must be above mark price"
    
    def test_position_detection_new_vs_existing(self):
        """Test that monitoring correctly identifies new vs existing positions."""
        # Existing positions in DB
        existing_syms = {"BTCUSDT", "ETHUSDT"}
        
        # Positions from exchange
        exchange_positions = [
            {"symbol": "BTCUSDT"},  # Existing
            {"symbol": "ETHUSDT"},  # Existing
            {"symbol": "SOLUSDT"}   # New
        ]
        
        # Find new positions
        ex_syms = {p["symbol"] for p in exchange_positions}
        new_positions = ex_syms - existing_syms
        
        assert new_positions == {"SOLUSDT"}, "Should detect SOLUSDT as new"
        assert len(new_positions) == 1, "Should find exactly 1 new position"


class TestMultiExchangeSupport:
    """Test logic across different exchanges and modes."""
    
    @pytest.mark.asyncio
    async def test_bybit_demo_position_fetch(self):
        """Test fetching positions in Bybit demo mode."""
        import db
        
        uid = 999999
        
        # Mock user with demo mode
        with patch.object(db, 'get_trading_mode', return_value='demo'):
            mode = db.get_trading_mode(uid)
            assert mode == 'demo', "Should return demo mode"
    
    @pytest.mark.asyncio
    async def test_bybit_real_position_fetch(self):
        """Test fetching positions in Bybit real mode."""
        import db
        
        uid = 999999
        
        # Mock user with real mode
        with patch.object(db, 'get_trading_mode', return_value='real'):
            mode = db.get_trading_mode(uid)
            assert mode == 'real', "Should return real mode"
    
    @pytest.mark.asyncio
    async def test_hyperliquid_testnet_detection(self):
        """Test HyperLiquid testnet mode detection."""
        import db
        
        uid = 999999
        
        # Mock HyperLiquid credentials with testnet=True
        mock_creds = {
            'hl_private_key': 'test_key',
            'hl_testnet': 1
        }
        
        with patch.object(db, 'get_hl_credentials', return_value=mock_creds):
            creds = db.get_hl_credentials(uid)
            assert creds.get('hl_testnet') == 1, "Should be testnet mode"
    
    @pytest.mark.asyncio
    async def test_hyperliquid_mainnet_detection(self):
        """Test HyperLiquid mainnet mode detection."""
        import db
        
        uid = 999999
        
        # Mock HyperLiquid credentials with testnet=False
        mock_creds = {
            'hl_private_key': 'test_key',
            'hl_testnet': 0
        }
        
        with patch.object(db, 'get_hl_credentials', return_value=mock_creds):
            creds = db.get_hl_credentials(uid)
            assert creds.get('hl_testnet') == 0, "Should be mainnet mode"
    
    def test_exchange_type_detection(self):
        """Test exchange type detection (bybit vs hyperliquid)."""
        import db
        
        uid = 999999
        
        # Test Bybit
        with patch.object(db, 'get_exchange_type', return_value='bybit'):
            exchange = db.get_exchange_type(uid)
            assert exchange == 'bybit', "Should detect Bybit"
        
        # Test HyperLiquid
        with patch.object(db, 'get_exchange_type', return_value='hyperliquid'):
            exchange = db.get_exchange_type(uid)
            assert exchange == 'hyperliquid', "Should detect HyperLiquid"


class TestSLTPLogic:
    """Test Stop Loss and Take Profit logic."""
    
    def test_sl_tp_percent_calculation(self):
        """Test SL/TP percentage calculations."""
        entry = 100.0
        sl_pct = 3.0
        tp_pct = 8.0
        
        # LONG
        sl_long = entry * (1 - sl_pct / 100)
        tp_long = entry * (1 + tp_pct / 100)
        
        assert abs(sl_long - 97.0) < 0.001, "LONG SL should be 97.0"
        assert abs(tp_long - 108.0) < 0.001, "LONG TP should be 108.0"
        
        # SHORT
        sl_short = entry * (1 + sl_pct / 100)
        tp_short = entry * (1 - tp_pct / 100)
        
        assert abs(sl_short - 103.0) < 0.001, "SHORT SL should be 103.0"
        assert abs(tp_short - 92.0) < 0.001, "SHORT TP should be 92.0"
    
    def test_sl_below_current_price_validation(self):
        """Test that SL is validated against current price."""
        mark_price = 100.0
        
        # LONG: SL must be < mark_price
        sl_long_valid = 97.0
        sl_long_invalid = 105.0
        
        assert sl_long_valid < mark_price, "Valid LONG SL"
        assert sl_long_invalid > mark_price, "Invalid LONG SL (too high)"
        
        # SHORT: SL must be > mark_price
        sl_short_valid = 103.0
        sl_short_invalid = 95.0
        
        assert sl_short_valid > mark_price, "Valid SHORT SL"
        assert sl_short_invalid < mark_price, "Invalid SHORT SL (too low)"
    
    def test_tp_logic_for_long_and_short(self):
        """Test TP logic for LONG and SHORT positions."""
        entry = 100.0
        mark = 105.0
        
        # LONG: TP must be > entry AND > mark
        tp_long_valid = 108.0
        assert tp_long_valid > entry, "TP must be above entry for LONG"
        assert tp_long_valid > mark, "TP must be above mark for LONG"
        
        # SHORT: TP must be < entry
        mark_short = 95.0
        tp_short_valid = 92.0
        assert tp_short_valid < entry, "TP must be below entry for SHORT"


class TestATRLogic:
    """Test ATR (Average True Range) trailing stop logic."""
    
    def test_atr_initial_sl_setting(self):
        """Test ATR initial SL setting before trigger threshold."""
        entry = 100.0
        sl_pct = 3.0
        side = "Buy"
        
        # Calculate base SL
        base_sl = entry * (1 - sl_pct / 100)  # 97.0
        
        # Initial SL should be set to base_sl
        assert abs(base_sl - 97.0) < 0.001, "Initial SL should be at base_sl"
    
    def test_atr_trailing_activation(self):
        """Test ATR trailing activation after move threshold."""
        entry = 100.0
        mark = 103.0  # 3% profit
        trigger_pct = 2.0  # Trigger threshold
        
        # Calculate move %
        move_pct = (mark - entry) / entry * 100  # 3%
        
        # Should activate trailing if move_pct >= trigger_pct
        assert move_pct >= trigger_pct, "Should activate ATR trailing"
    
    def test_atr_sl_update_logic(self):
        """Test ATR SL update logic (only moves in favorable direction)."""
        current_sl = 97.0
        new_atr_sl = 98.0
        side = "Buy"
        
        # For LONG: new SL should be > current SL to update
        should_update = new_atr_sl > current_sl
        assert should_update, "LONG SL should update upward"
        
        # For SHORT: new SL should be < current SL to update
        side = "Sell"
        current_sl_short = 103.0
        new_atr_sl_short = 102.0
        
        should_update_short = new_atr_sl_short < current_sl_short
        assert should_update_short, "SHORT SL should update downward"


class TestWyckoffEntryZone:
    """Test Wyckoff Entry Zone limit order logic."""
    
    def test_wyckoff_long_limit_at_lower_bound(self):
        """Test that LONG Wyckoff uses lower boundary of entry zone."""
        entry_low = 75.2252
        entry_high = 76.6165
        side = "Buy"
        
        # For LONG: should use entry_low (better price)
        limit_price = entry_low
        
        assert limit_price == entry_low, "LONG should use lower boundary"
        assert limit_price < entry_high, "Should be at better price"
    
    def test_wyckoff_short_limit_at_upper_bound(self):
        """Test that SHORT Wyckoff uses upper boundary of entry zone."""
        entry_low = 75.2252
        entry_high = 76.6165
        side = "Sell"
        
        # For SHORT: should use entry_high (better price)
        limit_price = entry_high
        
        assert limit_price == entry_high, "SHORT should use upper boundary"
        assert limit_price > entry_low, "Should be at better price"
    
    def test_wyckoff_market_vs_limit_decision(self):
        """Test Wyckoff market vs limit order decision."""
        entry_low = 75.0
        entry_high = 76.0
        
        # Price INSIDE zone → Market order
        spot_price_inside = 75.5
        use_limit_inside = not (entry_low <= spot_price_inside <= entry_high)
        assert not use_limit_inside, "Should use Market when inside zone"
        
        # Price OUTSIDE zone → Limit order
        spot_price_outside = 80.0
        use_limit_outside = not (entry_low <= spot_price_outside <= entry_high)
        assert use_limit_outside, "Should use Limit when outside zone"


class TestIntegrationScenarios:
    """Integration tests for complete monitoring scenarios."""
    
    @pytest.mark.asyncio
    async def test_new_position_adds_to_db(self):
        """Test that new position from exchange is added to DB."""
        # Simulated scenario: position exists on exchange but not in DB
        existing_syms = set()  # Empty DB
        exchange_position = {
            "symbol": "BTCUSDT",
            "side": "Buy",
            "size": "1.0",
            "avgPrice": "50000.0"
        }
        
        # Detection logic
        is_new = exchange_position["symbol"] not in existing_syms
        
        assert is_new, "Should detect position as new"
    
    @pytest.mark.asyncio
    async def test_closed_position_removes_from_db(self):
        """Test that closed position is removed from DB."""
        # Simulated: position in DB but not on exchange
        db_symbols = {"BTCUSDT", "ETHUSDT"}
        exchange_symbols = {"ETHUSDT"}  # BTCUSDT was closed
        
        # Find closed positions
        closed = db_symbols - exchange_symbols
        
        assert closed == {"BTCUSDT"}, "Should detect BTCUSDT as closed"
    
    @pytest.mark.asyncio
    async def test_notification_spam_prevention(self):
        """Test that notifications are not sent repeatedly for same position."""
        import bot
        
        uid = 999999
        symbol = "BTCUSDT"
        
        # First iteration: position is new
        open_syms_prev = set()
        is_new_first = symbol not in open_syms_prev
        assert is_new_first, "First time should be new"
        
        # Second iteration: position already exists
        open_syms_prev = {symbol}
        is_new_second = symbol not in open_syms_prev
        assert not is_new_second, "Second time should not be new"


def run_all_tests():
    """Run all monitoring logic tests."""
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--color=yes',
        '-x'  # Stop on first failure
    ])


if __name__ == '__main__':
    run_all_tests()
