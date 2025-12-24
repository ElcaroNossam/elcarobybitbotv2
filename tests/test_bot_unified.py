"""
Integration tests for bot_unified.py
Tests unified trading functions
"""
import unittest
import sys
import os
import asyncio
from unittest.mock import Mock, patch, AsyncMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from bot_unified import (
    get_balance_unified,
    get_positions_unified,
    place_order_unified,
    close_position_unified,
    set_leverage_unified
)
from models.unified import Position, Balance, OrderResult, PositionSide


class TestBotUnified(unittest.TestCase):
    """Test bot_unified trading functions"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.user_id = 12345
        self.symbol = "BTCUSDT"
    
    @patch('core.exchange_client.get_exchange_client')
    def test_get_balance_bybit(self, mock_get_client):
        """Test get_balance_unified for Bybit"""
        # Mock exchange client - return dict as client.get_balance() returns
        mock_client = AsyncMock()
        mock_client.get_balance.return_value = {
            'success': True,
            'data': {
                'total_equity': 100000.0,
                'available_balance': 80000.0,
                'margin_used': 15000.0,
                'unrealized_pnl': 5000.0,
                'currency': 'USDT'
            }
        }
        mock_get_client.return_value = mock_client
        
        # Run async test
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            get_balance_unified(self.user_id, "bybit", "demo")
        )
        
        # get_balance_unified returns Balance object
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Balance)
        self.assertEqual(result.total_equity, 100000.0)
        self.assertEqual(result.available_balance, 80000.0)
    
    @patch('core.exchange_client.get_exchange_client')
    def test_get_positions_bybit(self, mock_get_client):
        """Test get_positions_unified for Bybit"""
        # Mock exchange client
        mock_client = AsyncMock()
        from models.unified import PositionSide
        mock_client.get_positions.return_value = [
            Position(
                symbol="BTCUSDT",
                side=PositionSide.LONG,
                size=0.5,
                entry_price=50000.0,
                mark_price=51000.0,
                leverage=10,
                unrealized_pnl=500.0,
                exchange="bybit"
            )
        ]
        mock_get_client.return_value = mock_client
        
        # Run async test
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            get_positions_unified(self.user_id, "bybit", "demo")
        )
        
        # get_positions_unified returns a list directly
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].symbol, "BTCUSDT")
        self.assertEqual(result[0].side, PositionSide.LONG)
    
    @patch('core.exchange_client.get_exchange_client')
    def test_place_order_bybit(self, mock_get_client):
        """Test place_order_unified for Bybit"""
        # Mock exchange client
        mock_client = AsyncMock()
        mock_client.place_order.return_value = OrderResult(
            success=True,
            order_id="order-123",
            exchange="bybit"
        )
        mock_get_client.return_value = mock_client
        
        # Run async test
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            place_order_unified(
                user_id=self.user_id,
                symbol="BTCUSDT",
                side="buy",
                order_type="market",
                qty=0.5,
                exchange="bybit",
                account_type="demo"
            )
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["order_id"], "order-123")
    
    @patch('bot_unified.get_positions_unified')
    @patch('core.exchange_client.get_exchange_client')
    def test_close_position_bybit(self, mock_get_client, mock_get_positions):
        """Test close_position_unified for Bybit"""
        # Mock get_positions to return existing position
        mock_get_positions.return_value = [
            Position(
                symbol="BTCUSDT",
                side=PositionSide.LONG,
                size=0.5,
                entry_price=50000.0,
                mark_price=51000.0,
                leverage=10,
                unrealized_pnl=500.0,
                exchange="bybit"
            )
        ]
        
        # Mock exchange client
        mock_client = AsyncMock()
        mock_client.place_order.return_value = OrderResult(
            success=True,
            order_id="close-order-123",
            exchange="bybit"
        )
        mock_get_client.return_value = mock_client
        
        # Run async test
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            close_position_unified(
                user_id=self.user_id,
                symbol="BTCUSDT",
                exchange="bybit",
                account_type="demo"
            )
        )
        
        self.assertTrue(result["success"])
    
    @patch('core.exchange_client.get_exchange_client')
    def test_set_leverage_bybit(self, mock_get_client):
        """Test set_leverage_unified for Bybit"""
        # Mock exchange client
        mock_client = AsyncMock()
        mock_client.set_leverage.return_value = {
            "success": True,
            "message": "Leverage set to 10x"
        }
        mock_get_client.return_value = mock_client
        
        # Run async test
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            set_leverage_unified(
                user_id=self.user_id,
                symbol="BTCUSDT",
                leverage=10,
                exchange="bybit",
                account_type="demo"
            )
        )
        
        # set_leverage_unified returns bool directly
        self.assertTrue(result)
    
    @patch('core.exchange_client.get_exchange_client')
    def test_error_handling(self, mock_get_client):
        """Test error handling in unified functions"""
        # Mock client to raise exception
        mock_client = AsyncMock()
        mock_client.get_balance.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client
        
        # Run async test
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            get_balance_unified(self.user_id, "bybit", "demo")
        )
        
        # Function should return None on error
        self.assertIsNone(result)


class TestHyperLiquidIntegration(unittest.TestCase):
    """Test HyperLiquid integration in bot_unified"""
    
    def setUp(self):
        self.user_id = 12345
    
    @patch('core.exchange_client.get_exchange_client')
    def test_get_balance_hyperliquid(self, mock_get_client):
        """Test get_balance_unified for HyperLiquid"""
        # Mock HL client
        mock_client = AsyncMock()
        mock_client.get_balance.return_value = Balance(
            total_equity=50000.0,
            available_balance=40000.0,
            margin_used=8000.0,
            unrealized_pnl=2000.0,
            currency="USDC",
            exchange="hyperliquid",
            account_type="real"
        )
        mock_get_client.return_value = mock_client
        
        # Run async test
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            get_balance_unified(self.user_id, "hyperliquid", "real")
        )
        
        # get_balance_unified returns Balance object directly (or None)
        self.assertIsNotNone(result)
        self.assertEqual(result.total_equity, 50000.0)
        self.assertEqual(result.exchange, "hyperliquid")


if __name__ == "__main__":
    unittest.main()
