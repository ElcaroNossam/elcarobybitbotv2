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
        
        # Elcaro: 50 - 25 = 25
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
        
        # Total: 225
        assert total_pnl == 225.00

    def test_position_not_in_db_uses_defaults(self):
        """Test API position without DB entry uses 'unknown' and 'bybit'."""
        from bot import build_pnl_summary_by_strategy_and_exchange
        
        api_positions = [
            {"symbol": "NEWCOIN", "unrealisedPnl": "50.00"}
        ]
        db_positions = []  # No DB entry for this position
        
        strategy_pnl, exchange_pnl, total_pnl = build_pnl_summary_by_strategy_and_exchange(
            api_positions, db_positions
        )
        
        # Should use 'unknown' strategy and 'bybit' exchange
        assert "unknown" in strategy_pnl
        assert strategy_pnl["unknown"]["pnl"] == 50.00
        
        assert "bybit" in exchange_pnl
        assert total_pnl == 50.00

    def test_null_pnl_treated_as_zero(self):
        """Test null/None PnL is treated as 0."""
        from bot import build_pnl_summary_by_strategy_and_exchange
        
        api_positions = [
            {"symbol": "BTCUSDT", "unrealisedPnl": None},
            {"symbol": "ETHUSDT", "unrealisedPnl": ""},
        ]
        db_positions = [
            {"symbol": "BTCUSDT", "strategy": "elcaro", "exchange": "bybit"},
            {"symbol": "ETHUSDT", "strategy": "elcaro", "exchange": "bybit"},
        ]
        
        strategy_pnl, exchange_pnl, total_pnl = build_pnl_summary_by_strategy_and_exchange(
            api_positions, db_positions
        )
        
        assert strategy_pnl["elcaro"]["pnl"] == 0.0
        assert total_pnl == 0.0

    def test_negative_pnl(self):
        """Test handling of negative PnL values."""
        from bot import build_pnl_summary_by_strategy_and_exchange
        
        api_positions = [
            {"symbol": "BTCUSDT", "unrealisedPnl": "-100.00"},
            {"symbol": "ETHUSDT", "unrealisedPnl": "-50.00"},
            {"symbol": "SOLUSDT", "unrealisedPnl": "-50.00"},
        ]
        db_positions = [
            {"symbol": "BTCUSDT", "strategy": "fibonacci", "exchange": "bybit"},
            {"symbol": "ETHUSDT", "strategy": "fibonacci", "exchange": "bybit"},
            {"symbol": "SOLUSDT", "strategy": "fibonacci", "exchange": "bybit"},
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
        assert "+100.50" in result
        assert "(3)" in result
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


class TestPositionTranslationKeys:
    """Tests for position-related translation keys."""

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
