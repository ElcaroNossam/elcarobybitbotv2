"""
Unit tests for unified data models
Tests converters from Bybit/HyperLiquid to unified format
"""
import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.unified import Position, Order, Balance, OrderResult, OrderSide, OrderType, normalize_symbol


class TestNormalizeSymbol(unittest.TestCase):
    """Test symbol normalization"""
    
    def test_normalize_btc(self):
        self.assertEqual(normalize_symbol("BTC"), "BTCUSDT")
        self.assertEqual(normalize_symbol("BTCUSD"), "BTCUSDT")
        self.assertEqual(normalize_symbol("BTCUSDT"), "BTCUSDT")
    
    def test_normalize_eth(self):
        self.assertEqual(normalize_symbol("ETH"), "ETHUSDT")
        self.assertEqual(normalize_symbol("ETHUSDT"), "ETHUSDT")
    
    def test_lowercase(self):
        self.assertEqual(normalize_symbol("btc"), "BTCUSDT")
        self.assertEqual(normalize_symbol("eth"), "ETHUSDT")


class TestPositionConversion(unittest.TestCase):
    """Test Position dataclass conversions"""
    
    def test_from_bybit(self):
        """Test Bybit position conversion"""
        bybit_pos = {
            "symbol": "BTCUSDT",
            "side": "Buy",
            "size": "0.5",
            "avgPrice": "50000.0",
            "markPrice": "51000.0",
            "leverage": "10",
            "unrealisedPnl": "500.0",
            "takeProfit": "55000.0",
            "stopLoss": "48000.0",
            "positionValue": "25000.0",
            "liqPrice": "45000.0",
            "createdTime": "1234567890"
        }
        
        pos = Position.from_bybit(bybit_pos)
        
        self.assertEqual(pos.symbol, "BTCUSDT")
        self.assertEqual(pos.side.value, "Buy")  # PositionSide enum
        self.assertEqual(pos.size, 0.5)
        self.assertEqual(pos.entry_price, 50000.0)
        self.assertEqual(pos.mark_price, 51000.0)
        self.assertEqual(pos.leverage, 10)
        self.assertEqual(pos.unrealized_pnl, 500.0)
        self.assertEqual(pos.take_profit, 55000.0)
        self.assertEqual(pos.stop_loss, 48000.0)
        self.assertEqual(pos.exchange, "bybit")
    
    def test_from_bybit_short(self):
        """Test Bybit short position"""
        bybit_pos = {
            "symbol": "ETHUSDT",
            "side": "Sell",
            "size": "1.0",
            "avgPrice": "3000.0"
        }
        
        pos = Position.from_bybit(bybit_pos)
        self.assertEqual(pos.side.value, "Sell")  # PositionSide.SHORT
        self.assertEqual(pos.size, 1.0)
    
    def test_from_hyperliquid(self):
        """Test HyperLiquid position conversion"""
        hl_pos = {
            "position": {
                "coin": "BTC",
                "szi": "0.3",  # Positive = long
                "entryPx": "52000.0",
                "unrealizedPnl": "300.0",
                "leverage": {"value": 5},
                "marginUsed": "3000.0"
            },
            "markPx": "53000.0"
        }
        
        pos = Position.from_hyperliquid(hl_pos)
        
        self.assertEqual(pos.symbol, "BTCUSD")  # HL format
        self.assertEqual(pos.side.value, "Buy")  # PositionSide.LONG
        self.assertEqual(pos.size, 0.3)
        self.assertEqual(pos.entry_price, 52000.0)
        self.assertEqual(pos.exchange, "hyperliquid")
    
    def test_to_dict(self):
        """Test Position serialization"""
        from models.unified import PositionSide
        
        pos = Position(
            symbol="BTCUSDT",
            side=PositionSide.LONG,  # Use enum
            size=0.5,
            entry_price=50000.0,
            mark_price=51000.0,
            leverage=10,
            unrealized_pnl=500.0,
            exchange="bybit"
        )
        
        d = pos.to_dict()
        
        self.assertIsInstance(d, dict)
        self.assertEqual(d["symbol"], "BTCUSDT")
        self.assertEqual(d["side"], "Buy")  # Enum value
        self.assertEqual(d["size"], 0.5)
        # pnl_percentage might not exist or calculated differently
        self.assertIn("pnl_percent", d)


class TestOrderConversion(unittest.TestCase):
    """Test Order dataclass conversions"""
    
    def test_from_bybit(self):
        """Test Bybit order conversion"""
        bybit_order = {
            "orderId": "order-123",
            "symbol": "BTCUSDT",
            "side": "Buy",
            "orderType": "Limit",
            "price": "50000.0",
            "qty": "0.5",
            "cumExecQty": "0.2",
            "leavesQty": "0.3",
            "orderStatus": "PartiallyFilled",
            "createdTime": "1234567890000",
            "reduceOnly": False
        }
        
        order = Order.from_bybit(bybit_order)
        
        self.assertEqual(order.order_id, "order-123")
        self.assertEqual(order.symbol, "BTCUSDT")
        self.assertEqual(order.side.value, "Buy")  # Enum
        self.assertEqual(order.order_type.value, "Limit")  # Enum
        self.assertEqual(order.price, 50000.0)
        self.assertEqual(order.size, 0.5)
        self.assertEqual(order.filled_size, 0.2)
        self.assertEqual(order.status.value, "PartiallyFilled")
    
    def test_from_hyperliquid(self):
        """Test HyperLiquid order conversion"""
        hl_order = {
            "order": {
                "oid": 456,
                "coin": "ETH",
                "sz": "-1.0",  # Negative = sell
                "limitPx": "3000",
                "timestamp": 1234567890000
            }
        }
        
        order = Order.from_hyperliquid(hl_order)
        
        self.assertEqual(order.order_id, "456")
        self.assertEqual(order.symbol, "ETHUSD")  # HL format
        self.assertEqual(order.side.value, "Sell")  # Negative sz = sell


class TestBalanceConversion(unittest.TestCase):
    """Test Balance dataclass conversions"""
    
    def test_from_bybit(self):
        """Test Bybit balance conversion"""
        bybit_balance = {
            "totalEquity": "100000.0",
            "totalAvailableBalance": "80000.0",
            "totalPerpUPL": "5000.0",
            "totalMarginBalance": "95000.0",
            "accountType": "UNIFIED"
        }
        
        balance = Balance.from_bybit(bybit_balance)
        
        self.assertEqual(balance.total_equity, 100000.0)
        self.assertEqual(balance.available_balance, 80000.0)
        self.assertEqual(balance.unrealized_pnl, 5000.0)
        self.assertEqual(balance.exchange, "bybit")
        self.assertEqual(balance.account_type, "unified")
    
    def test_from_hyperliquid(self):
        """Test HyperLiquid balance conversion"""
        hl_balance = {
            "marginSummary": {
                "accountValue": "50000.0",
                "totalMarginUsed": "10000.0",
                "withdrawable": "40000.0",
                "totalNtlPos": "2000.0"
            }
        }
        
        balance = Balance.from_hyperliquid(hl_balance)
        
        self.assertEqual(balance.total_equity, 50000.0)
        self.assertEqual(balance.available_balance, 40000.0)  # withdrawable
        self.assertEqual(balance.margin_used, 10000.0)
        self.assertEqual(balance.currency, "USDC")


class TestOrderResult(unittest.TestCase):
    """Test OrderResult dataclass"""
    
    def test_success(self):
        """Test successful order result"""
        from models.unified import OrderSide, OrderType, OrderStatus
        
        test_order = Order(
            order_id="order-123",
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            size=0.5,
            status=OrderStatus.FILLED,
            filled_size=0.5
        )
        
        result = OrderResult.success_result(test_order, exchange="bybit")
        
        self.assertTrue(result.success)
        self.assertEqual(result.order_id, "order-123")
        self.assertIsNone(result.error)
        self.assertEqual(result.exchange, "bybit")
    
    def test_error(self):
        """Test error order result"""
        result = OrderResult(
            success=False,
            error="Insufficient balance"
        )
        
        self.assertFalse(result.success)
        self.assertEqual(result.error, "Insufficient balance")
        self.assertIsNone(result.order_id)


if __name__ == "__main__":
    unittest.main()
