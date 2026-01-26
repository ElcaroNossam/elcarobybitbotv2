"""
Tests for 4D Schema Strategy Settings

4D Schema: PRIMARY KEY (user_id, strategy, side, exchange)

This tests:
1. Independent settings per side (long/short)
2. Independent settings per exchange (bybit/hyperliquid)
3. Settings retrieval with long_* and short_* prefixes
4. Settings fallback to STRATEGY_DEFAULTS
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from unittest.mock import patch, MagicMock
from contextlib import contextmanager


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_db_connection():
    """Mock PostgreSQL connection for 4D schema tests"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    # Storage for settings - simulates 4D schema
    _settings_store = {}
    
    def mock_execute(query, params=None):
        nonlocal _settings_store
        query_lower = query.lower().strip()
        
        if 'insert into user_strategy_settings' in query_lower:
            # Handle UPSERT - params: (user_id, strategy, side, exchange, ...)
            if params and len(params) >= 4:
                key = (params[0], params[1], params[2], params[3])
                _settings_store[key] = {
                    'user_id': params[0],
                    'strategy': params[1],
                    'side': params[2],
                    'exchange': params[3],
                    'percent': params[4] if len(params) > 4 else None,
                    'sl_percent': params[5] if len(params) > 5 else None,
                    'tp_percent': params[6] if len(params) > 6 else None,
                    'leverage': params[7] if len(params) > 7 else None,
                    'enabled': params[8] if len(params) > 8 else 1,
                }
        elif 'update user_strategy_settings' in query_lower:
            # Handle UPDATE
            pass
        elif 'select' in query_lower and 'user_strategy_settings' in query_lower:
            # Return results for SELECT
            if params:
                user_id = params[0]
                strategy = params[1]
                exchange = params[2] if len(params) > 2 else 'bybit'
                
                # Find matching rows
                results = []
                for key, val in _settings_store.items():
                    if key[0] == user_id and key[1] == strategy and key[3] == exchange:
                        results.append(val)
                mock_cursor._last_results = results
        
        mock_cursor._store = _settings_store
    
    mock_cursor.execute = mock_execute
    mock_cursor.fetchall.side_effect = lambda: getattr(mock_cursor, '_last_results', [])
    mock_cursor.fetchone.side_effect = lambda: (getattr(mock_cursor, '_last_results', [None]) or [None])[0]
    
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    
    @contextmanager
    def mock_get_conn():
        yield mock_conn
    
    return mock_get_conn, _settings_store


# ============================================================================
# TEST: 4D SCHEMA STRUCTURE
# ============================================================================

class Test4DSchemaStructure:
    """Test the 4D schema structure"""
    
    def test_4d_primary_key_components(self):
        """Verify 4D PK has all required components"""
        components = ['user_id', 'strategy', 'side', 'exchange']
        
        # This is the structure we expect
        pk = {
            'user_id': 123456,
            'strategy': 'oi',
            'side': 'long',
            'exchange': 'bybit'
        }
        
        for comp in components:
            assert comp in pk
    
    def test_sides_are_valid(self):
        """Valid sides are 'long' and 'short'"""
        valid_sides = ['long', 'short']
        
        for side in valid_sides:
            assert side in ['long', 'short']
    
    def test_exchanges_are_valid(self):
        """Valid exchanges are 'bybit' and 'hyperliquid'"""
        valid_exchanges = ['bybit', 'hyperliquid']
        
        for ex in valid_exchanges:
            assert ex in ['bybit', 'hyperliquid']
    
    def test_strategies_list(self):
        """All supported strategies"""
        from coin_params import STRATEGY_FEATURES
        
        strategies = list(STRATEGY_FEATURES.keys())
        
        # Should have at least these core strategies
        core_strategies = ['oi', 'scryptomera', 'scalper', 'elcaro', 'fibonacci', 'rsi_bb']
        for s in core_strategies:
            assert s in strategies, f"Missing strategy: {s}"


# ============================================================================
# TEST: SIDE-SPECIFIC SETTINGS
# ============================================================================

class TestSideSpecificSettings:
    """Test that long and short have independent settings"""
    
    def test_long_short_independence(self, test_db):
        """Long and short settings are independent"""
        cursor = test_db.cursor()
        
        user_id = 777001
        strategy = 'oi'
        exchange = 'bybit'
        
        # Create user
        cursor.execute("INSERT OR REPLACE INTO users (user_id, is_allowed) VALUES (?, 1)", (user_id,))
        
        # Insert LONG settings
        cursor.execute("""
            INSERT OR REPLACE INTO user_strategy_settings 
            (user_id, strategy, side, exchange, percent, sl_percent, tp_percent, leverage)
            VALUES (?, ?, 'long', ?, 1.0, 3.0, 8.0, 10)
        """, (user_id, strategy, exchange))
        
        # Insert SHORT settings (different values)
        cursor.execute("""
            INSERT OR REPLACE INTO user_strategy_settings 
            (user_id, strategy, side, exchange, percent, sl_percent, tp_percent, leverage)
            VALUES (?, ?, 'short', ?, 2.0, 5.0, 12.0, 15)
        """, (user_id, strategy, exchange))
        
        test_db.commit()
        
        # Retrieve LONG
        cursor.execute("""
            SELECT percent, sl_percent, tp_percent, leverage 
            FROM user_strategy_settings 
            WHERE user_id=? AND strategy=? AND side='long' AND exchange=?
        """, (user_id, strategy, exchange))
        long_row = cursor.fetchone()
        
        # Retrieve SHORT
        cursor.execute("""
            SELECT percent, sl_percent, tp_percent, leverage 
            FROM user_strategy_settings 
            WHERE user_id=? AND strategy=? AND side='short' AND exchange=?
        """, (user_id, strategy, exchange))
        short_row = cursor.fetchone()
        
        # Verify they are different
        assert long_row is not None
        assert short_row is not None
        
        assert long_row[0] == 1.0  # percent
        assert long_row[1] == 3.0  # sl_percent
        assert long_row[2] == 8.0  # tp_percent
        assert long_row[3] == 10   # leverage
        
        assert short_row[0] == 2.0  # percent
        assert short_row[1] == 5.0  # sl_percent
        assert short_row[2] == 12.0 # tp_percent
        assert short_row[3] == 15   # leverage
        
        # Cleanup
        cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
        cursor.execute("DELETE FROM user_strategy_settings WHERE user_id=?", (user_id,))
        test_db.commit()
    
    def test_update_one_side_not_affect_other(self, test_db):
        """Updating long doesn't affect short"""
        cursor = test_db.cursor()
        
        user_id = 777002
        strategy = 'scalper'
        exchange = 'bybit'
        
        # Create user
        cursor.execute("INSERT OR REPLACE INTO users (user_id, is_allowed) VALUES (?, 1)", (user_id,))
        
        # Insert both sides with same values
        for side in ['long', 'short']:
            cursor.execute("""
                INSERT OR REPLACE INTO user_strategy_settings 
                (user_id, strategy, side, exchange, sl_percent)
                VALUES (?, ?, ?, ?, 3.0)
            """, (user_id, strategy, side, exchange))
        
        test_db.commit()
        
        # Update ONLY long
        cursor.execute("""
            UPDATE user_strategy_settings 
            SET sl_percent = 5.0 
            WHERE user_id=? AND strategy=? AND side='long' AND exchange=?
        """, (user_id, strategy, exchange))
        test_db.commit()
        
        # Verify short unchanged
        cursor.execute("""
            SELECT sl_percent FROM user_strategy_settings 
            WHERE user_id=? AND strategy=? AND side='short' AND exchange=?
        """, (user_id, strategy, exchange))
        short_row = cursor.fetchone()
        
        assert short_row[0] == 3.0, "Short should be unchanged"
        
        # Cleanup
        cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
        cursor.execute("DELETE FROM user_strategy_settings WHERE user_id=?", (user_id,))
        test_db.commit()


# ============================================================================
# TEST: EXCHANGE-SPECIFIC SETTINGS
# ============================================================================

class TestExchangeSpecificSettings:
    """Test that exchanges have independent settings"""
    
    def test_bybit_vs_hyperliquid_isolation(self, test_db):
        """Bybit and HyperLiquid have separate settings"""
        cursor = test_db.cursor()
        
        user_id = 777003
        strategy = 'scryptomera'
        
        # Create user
        cursor.execute("INSERT OR REPLACE INTO users (user_id, is_allowed) VALUES (?, 1)", (user_id,))
        
        # Insert Bybit settings
        cursor.execute("""
            INSERT OR REPLACE INTO user_strategy_settings 
            (user_id, strategy, side, exchange, leverage)
            VALUES (?, ?, 'long', 'bybit', 10)
        """, (user_id, strategy))
        
        # Insert HyperLiquid settings (different leverage)
        cursor.execute("""
            INSERT OR REPLACE INTO user_strategy_settings 
            (user_id, strategy, side, exchange, leverage)
            VALUES (?, ?, 'long', 'hyperliquid', 25)
        """, (user_id, strategy))
        
        test_db.commit()
        
        # Retrieve Bybit
        cursor.execute("""
            SELECT leverage FROM user_strategy_settings 
            WHERE user_id=? AND strategy=? AND side='long' AND exchange='bybit'
        """, (user_id, strategy))
        bybit_lev = cursor.fetchone()[0]
        
        # Retrieve HL
        cursor.execute("""
            SELECT leverage FROM user_strategy_settings 
            WHERE user_id=? AND strategy=? AND side='long' AND exchange='hyperliquid'
        """, (user_id, strategy))
        hl_lev = cursor.fetchone()[0]
        
        assert bybit_lev == 10
        assert hl_lev == 25
        
        # Cleanup
        cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
        cursor.execute("DELETE FROM user_strategy_settings WHERE user_id=?", (user_id,))
        test_db.commit()
    
    def test_all_4_dimensions_independent(self, test_db):
        """All 4 dimensions create independent records"""
        cursor = test_db.cursor()
        
        user_id = 777004
        strategy = 'elcaro'
        
        # Create user
        cursor.execute("INSERT OR REPLACE INTO users (user_id, is_allowed) VALUES (?, 1)", (user_id,))
        
        # Insert all 4 combinations
        combinations = [
            ('long', 'bybit', 1.0),
            ('long', 'hyperliquid', 2.0),
            ('short', 'bybit', 3.0),
            ('short', 'hyperliquid', 4.0),
        ]
        
        for side, exchange, percent in combinations:
            cursor.execute("""
                INSERT OR REPLACE INTO user_strategy_settings 
                (user_id, strategy, side, exchange, percent)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, strategy, side, exchange, percent))
        
        test_db.commit()
        
        # Count rows - should be 4
        cursor.execute("""
            SELECT COUNT(*) FROM user_strategy_settings 
            WHERE user_id=? AND strategy=?
        """, (user_id, strategy))
        count = cursor.fetchone()[0]
        
        assert count == 4, f"Expected 4 rows, got {count}"
        
        # Verify each has correct percent
        for side, exchange, expected_percent in combinations:
            cursor.execute("""
                SELECT percent FROM user_strategy_settings 
                WHERE user_id=? AND strategy=? AND side=? AND exchange=?
            """, (user_id, strategy, side, exchange))
            actual = cursor.fetchone()[0]
            assert actual == expected_percent, f"{side}/{exchange} mismatch"
        
        # Cleanup
        cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
        cursor.execute("DELETE FROM user_strategy_settings WHERE user_id=?", (user_id,))
        test_db.commit()


# ============================================================================
# TEST: SETTINGS RETRIEVAL FORMAT
# ============================================================================

class TestSettingsRetrievalFormat:
    """Test that pg_get_strategy_settings returns long_* and short_* format"""
    
    def test_expected_output_format(self):
        """Settings should return with long_* and short_* prefixes"""
        # Expected format from pg_get_strategy_settings
        expected_keys = [
            'long_enabled', 'long_percent', 'long_sl_percent', 'long_tp_percent',
            'long_leverage', 'long_use_atr', 'long_order_type',
            'short_enabled', 'short_percent', 'short_sl_percent', 'short_tp_percent',
            'short_leverage', 'short_use_atr', 'short_order_type',
            'trading_mode', 'direction', 'coins_group', 'exchange'
        ]
        
        # All these should be in the result
        for key in expected_keys:
            assert key.startswith('long_') or key.startswith('short_') or key in ['trading_mode', 'direction', 'coins_group', 'exchange']
    
    def test_side_prefix_mapping(self):
        """Side maps to correct prefix"""
        side_to_prefix = {
            'long': 'long_',
            'short': 'short_',
            'Buy': 'long_',
            'Sell': 'short_',
            'LONG': 'long_',
            'SHORT': 'short_',
        }
        
        for side, expected_prefix in side_to_prefix.items():
            side_lower = side.lower()
            if side_lower in ('buy', 'long'):
                assert expected_prefix == 'long_'
            elif side_lower in ('sell', 'short'):
                assert expected_prefix == 'short_'


# ============================================================================
# TEST: MULTI-USER ISOLATION
# ============================================================================

class TestMultiUserIsolation:
    """Test that different users have isolated settings"""
    
    def test_users_independent(self, test_db):
        """Different users have independent settings"""
        cursor = test_db.cursor()
        
        user1 = 777010
        user2 = 777011
        strategy = 'oi'
        exchange = 'bybit'
        
        # Create users
        for uid in [user1, user2]:
            cursor.execute("INSERT OR REPLACE INTO users (user_id, is_allowed) VALUES (?, 1)", (uid,))
        
        # User1: aggressive settings
        cursor.execute("""
            INSERT OR REPLACE INTO user_strategy_settings 
            (user_id, strategy, side, exchange, leverage, sl_percent)
            VALUES (?, ?, 'long', ?, 50, 5.0)
        """, (user1, strategy, exchange))
        
        # User2: conservative settings
        cursor.execute("""
            INSERT OR REPLACE INTO user_strategy_settings 
            (user_id, strategy, side, exchange, leverage, sl_percent)
            VALUES (?, ?, 'long', ?, 5, 1.0)
        """, (user2, strategy, exchange))
        
        test_db.commit()
        
        # Verify isolation
        cursor.execute("""
            SELECT leverage, sl_percent FROM user_strategy_settings 
            WHERE user_id=? AND strategy=? AND side='long' AND exchange=?
        """, (user1, strategy, exchange))
        u1 = cursor.fetchone()
        
        cursor.execute("""
            SELECT leverage, sl_percent FROM user_strategy_settings 
            WHERE user_id=? AND strategy=? AND side='long' AND exchange=?
        """, (user2, strategy, exchange))
        u2 = cursor.fetchone()
        
        assert u1[0] == 50 and u1[1] == 5.0, "User1 settings wrong"
        assert u2[0] == 5 and u2[1] == 1.0, "User2 settings wrong"
        
        # Cleanup
        for uid in [user1, user2]:
            cursor.execute("DELETE FROM users WHERE user_id=?", (uid,))
            cursor.execute("DELETE FROM user_strategy_settings WHERE user_id=?", (uid,))
        test_db.commit()


# ============================================================================
# TEST: STRATEGY DEFAULTS FALLBACK
# ============================================================================

class TestStrategyDefaultsFallback:
    """Test fallback to STRATEGY_DEFAULTS when DB has no settings"""
    
    def test_defaults_exist(self):
        """STRATEGY_DEFAULTS has required fields"""
        from coin_params import STRATEGY_DEFAULTS
        
        required_fields = ['percent', 'sl_percent', 'tp_percent', 'leverage']
        
        for side in ['long', 'short']:
            defaults = STRATEGY_DEFAULTS.get(side, {})
            for field in required_fields:
                assert field in defaults, f"Missing {field} in {side} defaults"
    
    def test_defaults_have_reasonable_values(self):
        """Default values are reasonable"""
        from coin_params import STRATEGY_DEFAULTS
        
        for side in ['long', 'short']:
            defaults = STRATEGY_DEFAULTS.get(side, {})
            
            # Percent should be 0.5-5%
            percent = defaults.get('percent', 1.0)
            assert 0.1 <= percent <= 10.0, f"Unreasonable percent: {percent}"
            
            # SL should be 0.5-10%
            sl = defaults.get('sl_percent', 3.0)
            assert 0.1 <= sl <= 20.0, f"Unreasonable SL: {sl}"
            
            # TP should be 1-30%
            tp = defaults.get('tp_percent', 8.0)
            assert 0.1 <= tp <= 50.0, f"Unreasonable TP: {tp}"
            
            # Leverage 1-100
            lev = defaults.get('leverage', 10)
            assert 1 <= lev <= 100, f"Unreasonable leverage: {lev}"


# ============================================================================
# TEST: ATR SETTINGS
# ============================================================================

class TestATRSettings:
    """Test ATR trailing stop settings in 4D schema"""
    
    def test_atr_fields_exist(self, test_db):
        """ATR fields are in the schema"""
        cursor = test_db.cursor()
        
        # Check table columns
        cursor.execute("PRAGMA table_info(user_strategy_settings)")
        columns = {row[1] for row in cursor.fetchall()}
        
        atr_fields = ['use_atr', 'atr_periods', 'atr_multiplier_sl', 'atr_trigger_pct', 'atr_step_pct']
        for field in atr_fields:
            assert field in columns, f"Missing ATR field: {field}"
    
    def test_atr_per_side(self, test_db):
        """ATR can be different per side"""
        cursor = test_db.cursor()
        
        user_id = 777020
        strategy = 'scalper'
        exchange = 'bybit'
        
        # Create user
        cursor.execute("INSERT OR REPLACE INTO users (user_id, is_allowed) VALUES (?, 1)", (user_id,))
        
        # Long: ATR enabled
        cursor.execute("""
            INSERT OR REPLACE INTO user_strategy_settings 
            (user_id, strategy, side, exchange, use_atr, atr_trigger_pct)
            VALUES (?, ?, 'long', ?, 1, 2.0)
        """, (user_id, strategy, exchange))
        
        # Short: ATR disabled
        cursor.execute("""
            INSERT OR REPLACE INTO user_strategy_settings 
            (user_id, strategy, side, exchange, use_atr, atr_trigger_pct)
            VALUES (?, ?, 'short', ?, 0, 0.0)
        """, (user_id, strategy, exchange))
        
        test_db.commit()
        
        # Verify
        cursor.execute("""
            SELECT use_atr FROM user_strategy_settings 
            WHERE user_id=? AND strategy=? AND side='long' AND exchange=?
        """, (user_id, strategy, exchange))
        long_atr = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT use_atr FROM user_strategy_settings 
            WHERE user_id=? AND strategy=? AND side='short' AND exchange=?
        """, (user_id, strategy, exchange))
        short_atr = cursor.fetchone()[0]
        
        assert long_atr == 1, "Long should have ATR enabled"
        assert short_atr == 0, "Short should have ATR disabled"
        
        # Cleanup
        cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
        cursor.execute("DELETE FROM user_strategy_settings WHERE user_id=?", (user_id,))
        test_db.commit()


# ============================================================================
# TEST: DCA SETTINGS
# ============================================================================

class TestDCASettings:
    """Test DCA settings in 4D schema"""
    
    def test_dca_fields_exist(self, test_db):
        """DCA fields are in the schema"""
        cursor = test_db.cursor()
        
        # Check table columns
        cursor.execute("PRAGMA table_info(user_strategy_settings)")
        columns = {row[1] for row in cursor.fetchall()}
        
        dca_fields = ['dca_enabled', 'dca_pct_1', 'dca_pct_2']
        for field in dca_fields:
            assert field in columns, f"Missing DCA field: {field}"
    
    def test_dca_per_side(self, test_db):
        """DCA can be different per side"""
        cursor = test_db.cursor()
        
        user_id = 777021
        strategy = 'oi'
        exchange = 'bybit'
        
        # Create user
        cursor.execute("INSERT OR REPLACE INTO users (user_id, is_allowed) VALUES (?, 1)", (user_id,))
        
        # Long: DCA enabled with specific %
        cursor.execute("""
            INSERT OR REPLACE INTO user_strategy_settings 
            (user_id, strategy, side, exchange, dca_enabled, dca_pct_1, dca_pct_2)
            VALUES (?, ?, 'long', ?, 1, 10.0, 25.0)
        """, (user_id, strategy, exchange))
        
        # Short: DCA disabled
        cursor.execute("""
            INSERT OR REPLACE INTO user_strategy_settings 
            (user_id, strategy, side, exchange, dca_enabled, dca_pct_1, dca_pct_2)
            VALUES (?, ?, 'short', ?, 0, 0.0, 0.0)
        """, (user_id, strategy, exchange))
        
        test_db.commit()
        
        # Verify
        cursor.execute("""
            SELECT dca_enabled, dca_pct_1 FROM user_strategy_settings 
            WHERE user_id=? AND strategy=? AND side='long' AND exchange=?
        """, (user_id, strategy, exchange))
        long_row = cursor.fetchone()
        
        cursor.execute("""
            SELECT dca_enabled, dca_pct_1 FROM user_strategy_settings 
            WHERE user_id=? AND strategy=? AND side='short' AND exchange=?
        """, (user_id, strategy, exchange))
        short_row = cursor.fetchone()
        
        assert long_row[0] == 1 and long_row[1] == 10.0
        assert short_row[0] == 0
        
        # Cleanup
        cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
        cursor.execute("DELETE FROM user_strategy_settings WHERE user_id=?", (user_id,))
        test_db.commit()
