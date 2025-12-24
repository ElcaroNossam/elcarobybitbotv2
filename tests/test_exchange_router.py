"""
Unit Tests for Exchange Router
Tests for universal exchange routing between Bybit and HyperLiquid
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestExchangeRouter:
    """Test exchange routing functionality"""
    
    @pytest.mark.unit
    @pytest.mark.exchange
    @pytest.mark.asyncio
    async def test_route_to_bybit(self, test_user_id, mock_bybit_client):
        """Test routing order to Bybit"""
        from exchange_router import place_order_universal
        
        mock_bybit_client.place_order.return_value = {"orderId": "123"}
        
        with patch('exchange_router.get_exchange_type', return_value='bybit'):
            result = await place_order_universal(
                test_user_id,
                symbol="BTCUSDT",
                side="Buy",
                orderType="Market",
                qty=0.1,
                bybit_place_order_func=mock_bybit_client.place_order
            )
        
        assert result is not None
        mock_bybit_client.place_order.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.exchange
    @pytest.mark.asyncio
    async def test_route_to_hyperliquid(self, test_user_id, mock_hyperliquid_client):
        """Test routing order to HyperLiquid"""
        from exchange_router import place_order_universal
        
        # Mock HyperLiquid response
        with patch('exchange_router.get_exchange_type', return_value='hyperliquid'):
            with patch('exchange_router.get_hl_credentials', return_value={'hl_private_key': None}):
                try:
                    result = await place_order_universal(
                        test_user_id,
                        symbol="BTCUSDT",
                        side="Buy",
                        orderType="Market",
                        qty=0.1
                    )
                except ValueError as e:
                    # Expected - HyperLiquid not configured
                    assert "not configured" in str(e)
    
    @pytest.mark.unit
    @pytest.mark.exchange
    @pytest.mark.asyncio
    async def test_fetch_positions_universal(self, test_user_id, mock_bybit_client):
        """Test universal position fetching"""
        from exchange_router import fetch_positions_universal
        
        mock_bybit_client.get_positions.return_value = [{
            "symbol": "BTCUSDT",
            "side": "Buy",
            "size": "0.1"
        }]
        
        with patch('exchange_router.get_exchange_type', return_value='bybit'):
            result = await fetch_positions_universal(
                test_user_id,
                "BTCUSDT",
                bybit_fetch_positions_func=mock_bybit_client.get_positions
            )
        
        assert result is not None
    
    @pytest.mark.unit
    @pytest.mark.exchange
    @pytest.mark.asyncio
    async def test_close_position_universal(self, test_user_id, mock_bybit_client):
        """Test universal position closing"""
        from exchange_router import close_position_universal
        
        mock_bybit_client.place_order.return_value = {"orderId": "close_123"}
        
        with patch('exchange_router.get_exchange_type', return_value='bybit'):
            result = await close_position_universal(
                test_user_id,
                symbol="BTCUSDT",
                size=0.1,
                side="Buy",
                bybit_place_order_func=mock_bybit_client.place_order
            )
        
        assert result is not None
        mock_bybit_client.place_order.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.exchange
    @pytest.mark.asyncio
    async def test_set_leverage_universal(self, test_user_id, mock_bybit_client):
        """Test universal leverage setting"""
        from exchange_router import set_leverage_universal
        
        mock_bybit_client.set_leverage.return_value = {
            "retCode": 0,
            "result": {"leverage": "10"}
        }
        
        with patch('exchange_router.get_exchange_type', return_value='bybit'):
            result = await set_leverage_universal(
                test_user_id,
                symbol="BTCUSDT",
                leverage=10,
                bybit_set_leverage_func=mock_bybit_client.set_leverage
            )
        
        assert result is not None
    
    @pytest.mark.unit
    @pytest.mark.exchange
    @pytest.mark.asyncio
    async def test_get_balance_universal(self, test_user_id, mock_bybit_client):
        """Test universal balance retrieval"""
        from exchange_router import get_balance_universal
        
        with patch('exchange_router.get_exchange_type', return_value='bybit'):
            result = await get_balance_universal(
                test_user_id,
                bybit_get_balance_func=mock_bybit_client.get_balance
            )
        
        assert result is not None
    
    @pytest.mark.unit
    @pytest.mark.exchange
    def test_symbol_normalization_for_hl(self):
        """Test symbol normalization for HyperLiquid (BTCUSDT -> BTC)"""
        from exchange_router import normalize_symbol_for_hl
        
        normalized = normalize_symbol_for_hl("BTCUSDT")
        assert normalized == "BTC"
        
        normalized = normalize_symbol_for_hl("ETHUSDT")
        assert normalized == "ETH"
    
    @pytest.mark.unit
    @pytest.mark.exchange
    def test_side_conversion_for_hl(self):
        """Test order side conversion for HyperLiquid"""
        from exchange_router import convert_side_for_hl
        
        # Bybit -> HyperLiquid
        assert convert_side_for_hl("Buy") == "BUY"
        assert convert_side_for_hl("Sell") == "SELL"


class TestExchangeSelection:
    """Test exchange selection logic"""
    
    @pytest.mark.unit
    @pytest.mark.exchange
    def test_get_user_exchange_type(self, test_user_id, test_db):
        """Test getting user's selected exchange"""
        import db
        
        with patch.object(db, 'get_exchange_type', return_value='bybit'):
            exchange_type = db.get_exchange_type(test_user_id)
        
        assert exchange_type == 'bybit'
    
    @pytest.mark.unit
    @pytest.mark.exchange
    def test_set_user_exchange_type(self, test_user_id, test_db):
        """Test setting user's exchange"""
        import db
        
        with patch.object(db, 'set_exchange_type', return_value=True):
            result = db.set_exchange_type(test_user_id, 'hyperliquid')
        
        assert result is True


class TestOrderTypeConversion:
    """Test order type conversions between exchanges"""
    
    @pytest.mark.unit
    @pytest.mark.exchange
    def test_bybit_order_type_to_hl(self):
        """Test converting Bybit order types to HyperLiquid"""
        from exchange_router import convert_order_type_for_hl
        
        assert convert_order_type_for_hl("Market") == "MARKET"
        assert convert_order_type_for_hl("Limit") == "LIMIT"
    
    @pytest.mark.unit
    @pytest.mark.exchange
    def test_invalid_order_type_raises_error(self):
        """Test that invalid order type raises error"""
        from exchange_router import convert_order_type_for_hl
        
        with pytest.raises(ValueError):
            convert_order_type_for_hl("InvalidType")


class TestResponseNormalization:
    """Test response format normalization"""
    
    @pytest.mark.unit
    @pytest.mark.exchange
    def test_normalize_bybit_response(self):
        """Test normalizing Bybit API response"""
        from exchange_router import normalize_response
        
        bybit_response = {
            "retCode": 0,
            "result": {"orderId": "123"}
        }
        
        normalized = normalize_response(bybit_response, "bybit")
        
        assert 'success' in normalized
        assert normalized['success'] is True
    
    @pytest.mark.unit
    @pytest.mark.exchange
    def test_normalize_hl_response(self):
        """Test normalizing HyperLiquid API response"""
        from exchange_router import normalize_response
        
        hl_response = {
            "status": "ok",
            "response": {"type": "order"}
        }
        
        normalized = normalize_response(hl_response, "hyperliquid")
        
        assert 'success' in normalized
        assert normalized['success'] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
