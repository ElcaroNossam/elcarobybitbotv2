"""
Quick Test to Verify Testing Infrastructure
"""

import pytest


def test_basic_math():
    """Verify basic Python operations"""
    assert 2 + 2 == 4
    assert 10 - 5 == 5
    assert 3 * 4 == 12


def test_string_operations():
    """Verify string operations"""
    text = "BTCUSDT"
    assert text.startswith("BTC")
    assert text.endswith("USDT")
    assert len(text) == 7


def test_list_operations():
    """Verify list operations"""
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    assert len(symbols) == 3
    assert "BTCUSDT" in symbols


@pytest.mark.asyncio
async def test_async_basic():
    """Verify async functionality"""
    import asyncio
    
    async def get_value():
        await asyncio.sleep(0.01)
        return 42
    
    result = await get_value()
    assert result == 42


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
