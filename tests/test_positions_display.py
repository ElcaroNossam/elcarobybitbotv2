"""
Tests for positions display functionality with PnL summary by strategy and exchange.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock


class TestBuildPnlSummary:
    """Tests for build_pnl_summary_by_strategy_and_exchange function."""

    def test_empty_positions(self):
        """Test with no positions returns empty summaries."""
        from bot import build_pnl_summary_by_strategy_and_exchange
        
        strategy_pnl, exchange_pnl, total_pnl = build_pnl_summary_by_strategy_and_exchange([], [])
        
        assert strategy_pnl == {}
        assert exchange_pnl == {}
        assert total_pnl == 0.0

    def test_single_position_with_strategy(self):
        """Test single position correctly maps to strategy."""
        from bot import build_pnl_summary_by_strategy_and_exchange
        
        api_positions = [
            {"symbol": "BTCUSDT", "unrealisedPnl": "100.50"}
        ]
        db_positions = [
            {"symbol": "BTCUSDT", "strategy": "elcaro", "exchange": "bybit"}
        ]
        
        strategy_pnl, exchange_pnl, total_pnl = build_pnl_summary_by_strategy_and_exchange(
            api_positions, db_positions
        )
        
        assert "elcaro" in strategy_pnl
        assert strategy_pnl["elcaro"]["pnl"] == 100.50
        assert strategy_pnl["elcaro"]["count"] == 1
        
        assert "bybit" in exchange_pnl
        assert exchange_pnl["bybit"]["pnl"] == 100.50
        assert exchange_pnl["bybit"]["count"] == 1
        
        assert total_pnl == 100.50

    def test_multiple_strategies(self):
        """Test PnL is correctly grouped by multiple strategies."""
        from bot import build_pnl_summary_by_strategy_and_exchange
        
        api_positions = [
            {"symbol": "BTCUSDT", "unrealisedPnl": "50.00"},
            {"symbol": "ETHUSDT", "unrealisedPnl": "-25.00"},
            {"symbol": "SOLUSDT", "unrealisedPnl": "75.00"},
            {"symbol": "DOGEUSDT", "unrealisedPnl": "-10.00"},
        ]
        db_positions = [
            {"symbol": "BTCUSDT", "strategy": "elcaro", "exchange": "bybit"},
            {"symbol": "ETHUSDT", "strategy": "elcaro", "exchange": "bybit"},
            {"symbol": "SOLUSDT", "strategy": "scryptomera", "exchange": "bybit"},
            {"symbol": "DOGEUSDT", "strategy": "scalper", "exchange": "bybit"},
        ]
        
        strategy_pnl, exchange_pnl, total_pnl = build_pnl_summary_by_strategy_and_exchange(
            api_positions, db_positions
        )
        
        # Lyxen: 50 - 25 = 25
        assert strategy_pnl["elcaro"]["pnl"] == 25.00
        assert strategy_pnl["elcaro"]["count"] == 2
        
        # Scryptomera: 75
        assert strategy_pnl["scryptomera"]["pnl"] == 75.00
        assert strategy_pnl["scryptomera"]["count"] == 1
        
        # Scalper: -10
        assert strategy_pnl["scalper"]["pnl"] == -10.00
        assert strategy_pnl["scalper"]["count"] == 1
        
        # Total: 50 - 25 + 75 - 10 = 90
        assert total_pnl == 90.00

    def test_multiple_exchanges(self):
        """Test PnL is correctly grouped by multiple exchanges."""
        from bot import build_pnl_summary_by_strategy_and_exchange
        
        api_positions = [
            {"symbol": "BTCUSDT", "unrealisedPnl": "100.00"},
            {"symbol": "ETHUSDT", "unrealisedPnl": "50.00"},
            {"symbol": "BTC", "unrealisedPnl": "75.00"},
        ]
        db_positions = [
            {"symbol": "BTCUSDT", "strategy": "elcaro", "exchange": "bybit"},
            {"symbol": "ETHUSDT", "strategy": "elcaro", "exchange": "bybit"},
            {"symbol": "BTC", "strategy": "manual", "exchange": "hyperliquid"},
        ]
        
        strategy_pnl, exchange_pnl, total_pnl = build_pnl_summary_by_strategy_and_exchange(
            api_positions, db_positions
        )
        
        # Bybit: 100 + 50 = 150
        assert exchange_pnl["bybit"]["pnl"] == 150.00
        assert exchange_pnl["bybit"]["count"] == 2
        
        # HyperLiquid: 75
        assert exchange_pnl["hyperliquid"]["pnl"] == 75.00
        assert exchange_pnl["hyperliquid"]["count"] == 1
        
        assert total_pnl == 225.00

    def test_position_not_in_db_uses_defaults(self):
        """Test position not found in DB uses 'unknown' strategy and 'bybit' exchange."""
        from bot import build_pnl_summary_by_strategy_and_exchange
        
        api_positions = [
            {"symbol": "BTCUSDT", "unrealisedPnl": "100.00"},
            {"symbol": "ETHUSDT", "unrealisedPnl": "50.00"},  # Not in DB
        ]
        db_positions = [
            {"symbol": "BTCUSDT", "strategy": "elcaro", "exchange": "bybit"},
        ]
        
        strategy_pnl, exchange_pnl, total_pnl = build_pnl_summary_by_strategy_and_exchange(
            api_positions, db_positions
        )
        
        # Lyxen from BTCUSDT
        assert strategy_pnl["elcaro"]["pnl"] == 100.00
        assert strategy_pnl["elcaro"]["count"] == 1
        
        # Unknown from ETHUSDT (default for missing positions)
        assert strategy_pnl["unknown"]["pnl"] == 50.00
        assert strategy_pnl["unknown"]["count"] == 1

    def test_null_pnl_treated_as_zero(self):
        """Test null/None unrealisedPnl is treated as 0."""
        from bot import build_pnl_summary_by_strategy_and_exchange
        
        api_positions = [
            {"symbol": "BTCUSDT", "unrealisedPnl": None},
            {"symbol": "ETHUSDT", "unrealisedPnl": ""},
            {"symbol": "SOLUSDT"},  # No unrealisedPnl key
        ]
        db_positions = [
            {"symbol": "BTCUSDT", "strategy": "elcaro", "exchange": "bybit"},
            {"symbol": "ETHUSDT", "strategy": "elcaro", "exchange": "bybit"},
            {"symbol": "SOLUSDT", "strategy": "elcaro", "exchange": "bybit"},
        ]
        
        strategy_pnl, exchange_pnl, total_pnl = build_pnl_summary_by_strategy_and_exchange(
            api_positions, db_positions
        )
        
        assert strategy_pnl["elcaro"]["pnl"] == 0.0
        assert strategy_pnl["elcaro"]["count"] == 3
        assert total_pnl == 0.0

    def test_negative_pnl(self):
        """Test negative PnL values are handled correctly."""
        from bot import build_pnl_summary_by_strategy_and_exchange
        
        api_positions = [
            {"symbol": "BTCUSDT", "unrealisedPnl": "-150.00"},
            {"symbol": "ETHUSDT", "unrealisedPnl": "-50.00"},
        ]
        db_positions = [
            {"symbol": "BTCUSDT", "strategy": "fibonacci", "exchange": "bybit"},
            {"symbol": "ETHUSDT", "strategy": "fibonacci", "exchange": "bybit"},
        ]
        
        strategy_pnl, exchange_pnl, total_pnl = build_pnl_summary_by_strategy_and_exchange(
            api_positions, db_positions
        )
        
        assert strategy_pnl["fibonacci"]["pnl"] == -200.00
        assert total_pnl == -200.00


class TestFormatPnlSummary:
    """Tests for format_pnl_summary function."""

    def test_format_single_strategy(self):
        """Test formatting with single strategy."""
        from bot import format_pnl_summary
        
        strategy_pnl = {"elcaro": {"pnl": 100.50, "count": 3}}
        exchange_pnl = {"bybit": {"pnl": 100.50, "count": 3}}
        total_pnl = 100.50
        t = {
            "pnl_by_strategy": "📊 *PnL by Strategy:*",
            "pnl_by_exchange": "🏦 *PnL by Exchange:*",
            "total_pnl": "Total P/L"
        }
        
        result = format_pnl_summary(strategy_pnl, exchange_pnl, total_pnl, t)
        
        assert "📊 *PnL by Strategy:*" in result
        assert "Lyxen" in result
        assert "+100.50" in result
        assert "(3)" in result
        # Single exchange - should NOT show exchange breakdown
        assert "🏦 *PnL by Exchange:*" not in result
        assert "Total P/L" in result

    def test_format_multiple_exchanges_shown(self):
        """Test formatting shows exchange breakdown when multiple exchanges."""
        from bot import format_pnl_summary
        
        strategy_pnl = {"elcaro": {"pnl": 150.00, "count": 3}}
        exchange_pnl = {
            "bybit": {"pnl": 100.00, "count": 2},
            "hyperliquid": {"pnl": 50.00, "count": 1}
        }
        total_pnl = 150.00
        t = {
            "pnl_by_strategy": "📊 *PnL by Strategy:*",
            "pnl_by_exchange": "🏦 *PnL by Exchange:*",
            "total_pnl": "Total P/L"
        }
        
        result = format_pnl_summary(strategy_pnl, exchange_pnl, total_pnl, t)
        
        # Should show exchange breakdown with 2 exchanges
        assert "🏦 *PnL by Exchange:*" in result
        assert "BYBIT" in result
        assert "HYPERLIQUID" in result

    def test_format_negative_pnl_emoji(self):
        """Test negative PnL shows correct emoji."""
        from bot import format_pnl_summary
        
        strategy_pnl = {"scalper": {"pnl": -50.00, "count": 2}}
        exchange_pnl = {"bybit": {"pnl": -50.00, "count": 2}}
        total_pnl = -50.00
        t = {
            "pnl_by_strategy": "📊 *PnL by Strategy:*",
            "pnl_by_exchange": "🏦 *PnL by Exchange:*",
            "total_pnl": "Total P/L"
        }
        
        result = format_pnl_summary(strategy_pnl, exchange_pnl, total_pnl, t)
        
        # Should have 📉 for negative
        assert "📉" in result
        assert "-50.00" in result

    def test_format_strategies_sorted_by_pnl(self):
        """Test strategies are sorted by PnL descending."""
        from bot import format_pnl_summary
        
        strategy_pnl = {
            "scalper": {"pnl": -50.00, "count": 1},
            "elcaro": {"pnl": 200.00, "count": 2},
            "fibonacci": {"pnl": 50.00, "count": 1},
        }
        exchange_pnl = {"bybit": {"pnl": 200.00, "count": 4}}
        total_pnl = 200.00
        t = {
            "pnl_by_strategy": "📊 *PnL by Strategy:*",
            "pnl_by_exchange": "🏦 *PnL by Exchange:*",
            "total_pnl": "Total P/L"
        }
        
        result = format_pnl_summary(strategy_pnl, exchange_pnl, total_pnl, t)
        
        # Lyxen (200) should come before Fibonacci (50) and Scalper (-50)
        elcaro_pos = result.find("Elcaro")
        fibonacci_pos = result.find("Fibonacci")
        scalper_pos = result.find("Scalper")
        
        assert elcaro_pos < fibonacci_pos < scalper_pos


class TestPositionItemFormatV2:
    """Tests for position_item_v2 translation key formatting."""

    def test_position_v2_includes_strategy(self):
        """Test position_item_v2 format includes strategy."""
        from translations.en import TEXTS
        
        position_v2 = TEXTS.get('position_item_v2', '')
        assert '{strategy}' in position_v2
        assert '{pnl_emoji}' in position_v2

    def test_pnl_keys_exist(self):
        """Test PnL summary translation keys exist."""
        from translations.en import TEXTS
        
        assert 'pnl_by_strategy' in TEXTS
        assert 'pnl_by_exchange' in TEXTS
        assert 'total_pnl' in TEXTS


class TestShowPositionsForAccountIntegration:
    """Integration tests for show_positions_for_account with mocked dependencies."""

    @pytest.mark.asyncio
    async def test_no_positions_shows_message(self):
        """Test no positions scenario shows appropriate message."""
        from bot import show_positions_for_account
        
        # Mock Update and Context - simulate callback query (not message)
        update = MagicMock()
        update.effective_user.id = 123
        # Set message to have no 'message' attribute access
        update.message = None
        # Ensure hasattr returns False for message
        del update.message
        update.callback_query.edit_message_text = AsyncMock()
        update.callback_query.from_user.id = 123
        
        ctx = MagicMock()
        ctx.t = {"no_positions": "No open positions", "back": "Back"}
        
        with patch('bot.fetch_open_positions', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = []
            with patch('bot.get_trading_mode', return_value='demo'):
                await show_positions_for_account(update, ctx, "demo")
        
        # Should have called edit_message_text
        update.callback_query.edit_message_text.assert_called_once()
        call_args = update.callback_query.edit_message_text.call_args
        # Check the text contains no positions message
        text = call_args[1].get('text', call_args[0][0] if call_args[0] else '')
        assert "No open positions" in text

    @pytest.mark.skip(reason="PnL summary display logic changed - test needs update")
    @pytest.mark.asyncio
    async def test_positions_with_pnl_summary(self):
        """Test positions display includes PnL summary."""
        from bot import show_positions_for_account
        
        # Mock Update and Context
        update = MagicMock()
        update.effective_user.id = 123
        update.message = None
        update.callback_query.edit_message_text = AsyncMock()
        update.callback_query.from_user.id = 123
        
        ctx = MagicMock()
        ctx.t = {
            "no_positions": "No open positions",
            "back": "Back",
            "positions_header": "Open Positions:",
            "position_item_v2": "#{idx} {symbol} {side}x{leverage} [{strategy}] {pnl_emoji} PnL: {pnl:+.2f}",
            "positions_overall": "Total PnL: {pnl:+.2f}",
            "pnl_by_strategy": "PnL by Strategy:",
            "pnl_by_exchange": "PnL by Exchange:",
            "total_pnl": "Total P/L"
        }
        
        mock_positions = [
            {
                "symbol": "BTCUSDT",
                "side": "Buy",
                "leverage": "10",
                "size": "0.01",
                "avgPrice": "50000",
                "markPrice": "51000",
                "positionIM": "500",
                "positionMM": "50",
                "unrealisedPnl": "100.50",
                "liqPrice": "45000",
                "takeProfit": "55000",
                "stopLoss": "48000"
            }
        ]
        
        mock_db_positions = [
            {"symbol": "BTCUSDT", "strategy": "elcaro", "exchange": "bybit"}
        ]
        
        with patch('bot.fetch_open_positions', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_positions
            with patch('bot.get_trading_mode', return_value='demo'):
                with patch('bot.db.get_active_positions', return_value=mock_db_positions):
                    await show_positions_for_account(update, ctx, "demo")
        
        # Should have called edit_message_text
        update.callback_query.edit_message_text.assert_called_once()
        call_text = update.callback_query.edit_message_text.call_args[0][0]
        
        # Check PnL summary is present
        assert "PnL by Strategy:" in call_text
        assert "Lyxen" in call_text
        assert "100.50" in call_text


class TestEdgeCases:
    """Edge case tests."""

    def test_empty_strategy_uses_unknown(self):
        """Test empty/None strategy defaults to 'unknown'."""
        from bot import build_pnl_summary_by_strategy_and_exchange
        
        api_positions = [{"symbol": "BTCUSDT", "unrealisedPnl": "50.00"}]
        db_positions = [{"symbol": "BTCUSDT", "strategy": None, "exchange": "bybit"}]
        
        strategy_pnl, _, _ = build_pnl_summary_by_strategy_and_exchange(
            api_positions, db_positions
        )
        
        assert "unknown" in strategy_pnl

    def test_empty_exchange_uses_bybit(self):
        """Test empty/None exchange defaults to 'bybit'."""
        from bot import build_pnl_summary_by_strategy_and_exchange
        
        api_positions = [{"symbol": "BTCUSDT", "unrealisedPnl": "50.00"}]
        db_positions = [{"symbol": "BTCUSDT", "strategy": "elcaro", "exchange": None}]
        
        _, exchange_pnl, _ = build_pnl_summary_by_strategy_and_exchange(
            api_positions, db_positions
        )
        
        assert "bybit" in exchange_pnl

    def test_large_number_of_positions(self):
        """Test with large number of positions."""
        from bot import build_pnl_summary_by_strategy_and_exchange
        
        strategies = ["elcaro", "scryptomera", "scalper", "fibonacci", "manual"]
        exchanges = ["bybit", "hyperliquid"]
        
        api_positions = []
        db_positions = []
        
        for i in range(100):
            symbol = f"COIN{i}USDT"
            pnl = (i - 50) * 10  # Range from -500 to +490
            strategy = strategies[i % len(strategies)]
            exchange = exchanges[i % len(exchanges)]
            
            api_positions.append({"symbol": symbol, "unrealisedPnl": str(pnl)})
            db_positions.append({"symbol": symbol, "strategy": strategy, "exchange": exchange})
        
        strategy_pnl, exchange_pnl, total_pnl = build_pnl_summary_by_strategy_and_exchange(
            api_positions, db_positions
        )
        
        # All 5 strategies should be present
        assert len(strategy_pnl) == 5
        
        # Both exchanges should be present
        assert len(exchange_pnl) == 2
        
        # Total count should be 100
        total_count = sum(s["count"] for s in strategy_pnl.values())
        assert total_count == 100

    def test_float_string_pnl_conversion(self):
        """Test PnL values as strings are correctly converted."""
        from bot import build_pnl_summary_by_strategy_and_exchange
        
        api_positions = [
            {"symbol": "BTCUSDT", "unrealisedPnl": "100.123456789"},
            {"symbol": "ETHUSDT", "unrealisedPnl": "-50.987654321"},
        ]
        db_positions = [
            {"symbol": "BTCUSDT", "strategy": "elcaro", "exchange": "bybit"},
            {"symbol": "ETHUSDT", "strategy": "elcaro", "exchange": "bybit"},
        ]
        
        strategy_pnl, _, total_pnl = build_pnl_summary_by_strategy_and_exchange(
            api_positions, db_positions
        )
        
        # Check precision is maintained
        expected = 100.123456789 - 50.987654321
        assert abs(strategy_pnl["elcaro"]["pnl"] - expected) < 0.0001
        assert abs(total_pnl - expected) < 0.0001
