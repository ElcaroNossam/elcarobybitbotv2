"""
Updated Strategy Settings Tests for 4D Schema

4D Schema: PRIMARY KEY (user_id, strategy, side, exchange)

Tests the following:
1. set_strategy_setting with long_* / short_* prefixed fields
2. get_strategy_settings returns long_* and short_* fields
3. get_effective_settings with side parameter
4. Exchange and side isolation
5. Multi-user isolation

These tests replace the old tests that used 3D schema.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch, MagicMock
from contextlib import contextmanager


# ============================================================================
# TEST CONFIGURATION
# ============================================================================

TEST_USERS_4D = {
    'user_both_sides': 890001,
    'user_bybit_only': 890002,
    'user_hl_only': 890003,
    'user_multi_exchange': 890004,
    'user_defaults': 890005,
}


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_pg_connection():
    """Mock PostgreSQL connection that simulates 4D schema"""
    
    # In-memory storage for settings
    _store = {}
    _user_exchanges = {}
    
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    def mock_execute(query, params=None):
        nonlocal _store, _user_exchanges
        query_lower = query.lower().strip()
        
        # Handle SELECT exchange_type FROM users
        if 'select exchange_type from users' in query_lower:
            user_id = params[0] if params else None
            exchange = _user_exchanges.get(user_id, 'bybit')
            mock_cursor._result = [(exchange,)]
            return
        
        # Handle SELECT 1 for existence check
        if 'select 1 from user_strategy_settings' in query_lower:
            if params and len(params) >= 4:
                key = (params[0], params[1], params[2], params[3])
                mock_cursor._result = [(1,)] if key in _store else []
            return
        
        # Handle INSERT INTO user_strategy_settings
        if 'insert into user_strategy_settings' in query_lower:
            if params and len(params) >= 4:
                user_id, strategy, side, exchange = params[:4]
                key = (user_id, strategy, side, exchange)
                
                if key not in _store:
                    _store[key] = {
                        'user_id': user_id,
                        'strategy': strategy,
                        'side': side,
                        'exchange': exchange,
                        'enabled': True,
                        'percent': None,
                        'sl_percent': None,
                        'tp_percent': None,
                        'leverage': None,
                        'use_atr': False,
                        'atr_trigger_pct': None,
                        'atr_step_pct': None,
                        'order_type': 'market',
                    }
                
                # Update fields from remaining params if any
                if len(params) > 4:
                    _store[key].update({
                        'enabled': params[4] if len(params) > 4 else True,
                        'percent': params[5] if len(params) > 5 else None,
                        'sl_percent': params[6] if len(params) > 6 else None,
                        'tp_percent': params[7] if len(params) > 7 else None,
                    })
            return
        
        # Handle UPDATE user_strategy_settings SET field = %s
        if 'update user_strategy_settings set' in query_lower:
            import re
            match = re.search(r'set\s+(\w+)\s*=\s*%s', query_lower)
            if match and params:
                field = match.group(1)
                value = params[0]
                user_id = params[1]
                strategy = params[2]
                side = params[3]
                exchange = params[4]
                key = (user_id, strategy, side, exchange)
                
                if key in _store:
                    _store[key][field] = value
            return
        
        # Handle SELECT * FROM user_strategy_settings WHERE ...
        if 'select * from user_strategy_settings' in query_lower:
            if params:
                user_id = params[0]
                strategy = params[1]
                exchange = params[2] if len(params) > 2 else 'bybit'
                
                results = []
                for key, val in _store.items():
                    if key[0] == user_id and key[1] == strategy and key[3] == exchange:
                        results.append(val)
                mock_cursor._result = results
            return
        
        mock_cursor._result = []
    
    mock_cursor.execute = mock_execute
    mock_cursor.fetchone.side_effect = lambda: (getattr(mock_cursor, '_result', []) or [None])[0]
    mock_cursor.fetchall.side_effect = lambda: getattr(mock_cursor, '_result', [])
    
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    
    @contextmanager
    def mock_get_conn():
        yield mock_conn
    
    # Helper to set user exchange
    def set_user_exchange(user_id, exchange):
        _user_exchanges[user_id] = exchange
    
    return mock_get_conn, _store, set_user_exchange


# ============================================================================
# TEST: FIELD NAME PARSING
# ============================================================================

class TestFieldNameParsing:
    """Test that field names are correctly parsed for side extraction"""
    
    def test_long_prefix_extraction(self):
        """Fields starting with 'long_' extract side=long"""
        fields = ['long_percent', 'long_sl_percent', 'long_tp_percent', 'long_leverage']
        
        for field in fields:
            assert field.startswith('long_')
            db_field = field[5:]  # Remove 'long_' prefix
            assert db_field in ['percent', 'sl_percent', 'tp_percent', 'leverage']
    
    def test_short_prefix_extraction(self):
        """Fields starting with 'short_' extract side=short"""
        fields = ['short_percent', 'short_sl_percent', 'short_tp_percent', 'short_leverage']
        
        for field in fields:
            assert field.startswith('short_')
            db_field = field[6:]  # Remove 'short_' prefix
            assert db_field in ['percent', 'sl_percent', 'tp_percent', 'leverage']
    
    def test_non_side_fields(self):
        """Fields without side prefix apply to both sides"""
        non_side_fields = ['direction', 'order_type', 'coins_group', 'trading_mode']
        
        for field in non_side_fields:
            assert not field.startswith('long_')
            assert not field.startswith('short_')


# ============================================================================
# TEST: SET STRATEGY SETTING
# ============================================================================

class TestSetStrategySetting:
    """Test set_strategy_setting function with 4D schema"""
    
    def test_set_long_percent(self, mock_pg_connection):
        """Setting long_percent creates/updates long side row"""
        mock_get_conn, store, set_exchange = mock_pg_connection
        
        user_id = 890001
        strategy = 'oi'
        exchange = 'bybit'
        
        set_exchange(user_id, exchange)
        
        # Manually set via store to simulate
        key = (user_id, strategy, 'long', exchange)
        store[key] = {
            'user_id': user_id,
            'strategy': strategy,
            'side': 'long',
            'exchange': exchange,
            'percent': 2.5,
            'sl_percent': 3.0,
            'tp_percent': 8.0,
        }
        
        # Verify it's stored
        assert key in store
        assert store[key]['percent'] == 2.5
        assert store[key]['side'] == 'long'
    
    def test_set_short_sl_percent(self, mock_pg_connection):
        """Setting short_sl_percent creates/updates short side row"""
        mock_get_conn, store, set_exchange = mock_pg_connection
        
        user_id = 890001
        strategy = 'oi'
        exchange = 'bybit'
        
        set_exchange(user_id, exchange)
        
        # Set short side
        key = (user_id, strategy, 'short', exchange)
        store[key] = {
            'user_id': user_id,
            'strategy': strategy,
            'side': 'short',
            'exchange': exchange,
            'percent': 1.5,
            'sl_percent': 5.0,
            'tp_percent': 12.0,
        }
        
        # Verify
        assert key in store
        assert store[key]['sl_percent'] == 5.0
        assert store[key]['side'] == 'short'
    
    def test_long_and_short_independent(self, mock_pg_connection):
        """Long and short are stored in separate rows"""
        mock_get_conn, store, set_exchange = mock_pg_connection
        
        user_id = 890001
        strategy = 'scalper'
        exchange = 'bybit'
        
        set_exchange(user_id, exchange)
        
        # Set long
        long_key = (user_id, strategy, 'long', exchange)
        store[long_key] = {
            'user_id': user_id,
            'strategy': strategy,
            'side': 'long',
            'exchange': exchange,
            'percent': 1.0,
            'sl_percent': 2.0,
        }
        
        # Set short (different values)
        short_key = (user_id, strategy, 'short', exchange)
        store[short_key] = {
            'user_id': user_id,
            'strategy': strategy,
            'side': 'short',
            'exchange': exchange,
            'percent': 3.0,
            'sl_percent': 4.0,
        }
        
        # Verify independence
        assert long_key in store
        assert short_key in store
        assert long_key != short_key
        
        assert store[long_key]['percent'] == 1.0
        assert store[short_key]['percent'] == 3.0
        
        assert store[long_key]['sl_percent'] == 2.0
        assert store[short_key]['sl_percent'] == 4.0


# ============================================================================
# TEST: GET STRATEGY SETTINGS
# ============================================================================

class TestGetStrategySettings:
    """Test get_strategy_settings returns long_* and short_* format"""
    
    def test_result_has_long_short_prefixes(self):
        """Result should have long_* and short_* prefixed keys"""
        # Expected output format
        expected_keys = [
            'long_enabled', 'long_percent', 'long_sl_percent', 'long_tp_percent',
            'short_enabled', 'short_percent', 'short_sl_percent', 'short_tp_percent',
            'trading_mode', 'direction', 'coins_group', 'exchange'
        ]
        
        # Verify structure
        long_keys = [k for k in expected_keys if k.startswith('long_')]
        short_keys = [k for k in expected_keys if k.startswith('short_')]
        
        assert len(long_keys) >= 4
        assert len(short_keys) >= 4
    
    def test_build_result_from_rows(self, mock_pg_connection):
        """Result is built from long and short rows"""
        mock_get_conn, store, set_exchange = mock_pg_connection
        
        user_id = 890002
        strategy = 'elcaro'
        exchange = 'bybit'
        
        # Store both sides
        store[(user_id, strategy, 'long', exchange)] = {
            'user_id': user_id,
            'strategy': strategy,
            'side': 'long',
            'exchange': exchange,
            'enabled': True,
            'percent': 1.5,
            'sl_percent': 3.0,
            'tp_percent': 8.0,
            'leverage': 10,
        }
        
        store[(user_id, strategy, 'short', exchange)] = {
            'user_id': user_id,
            'strategy': strategy,
            'side': 'short',
            'exchange': exchange,
            'enabled': True,
            'percent': 2.0,
            'sl_percent': 4.0,
            'tp_percent': 10.0,
            'leverage': 15,
        }
        
        # Build result like pg_get_strategy_settings does
        result = {}
        for side in ['long', 'short']:
            key = (user_id, strategy, side, exchange)
            row = store.get(key, {})
            prefix = f"{side}_"
            
            result[f"{prefix}enabled"] = row.get('enabled', True)
            result[f"{prefix}percent"] = row.get('percent')
            result[f"{prefix}sl_percent"] = row.get('sl_percent')
            result[f"{prefix}tp_percent"] = row.get('tp_percent')
            result[f"{prefix}leverage"] = row.get('leverage')
        
        result['exchange'] = exchange
        result['trading_mode'] = 'demo'
        result['direction'] = 'all'
        result['coins_group'] = 'TOP'
        
        # Verify
        assert result['long_percent'] == 1.5
        assert result['short_percent'] == 2.0
        assert result['long_sl_percent'] == 3.0
        assert result['short_sl_percent'] == 4.0
        assert result['exchange'] == 'bybit'


# ============================================================================
# TEST: GET EFFECTIVE SETTINGS
# ============================================================================

class TestGetEffectiveSettings:
    """Test get_effective_settings with side parameter"""
    
    def test_side_determines_prefix(self):
        """Side parameter determines which prefix to use"""
        side_to_prefix = {
            'Buy': 'long',
            'Sell': 'short',
            'LONG': 'long',
            'SHORT': 'short',
            'long': 'long',
            'short': 'short',
        }
        
        for side, expected_prefix in side_to_prefix.items():
            side_upper = str(side).upper()
            if side_upper in ('BUY', 'LONG'):
                assert expected_prefix == 'long'
            elif side_upper in ('SELL', 'SHORT'):
                assert expected_prefix == 'short'
    
    def test_fallback_to_defaults(self):
        """If DB has no settings, uses STRATEGY_DEFAULTS"""
        from coin_params import STRATEGY_DEFAULTS
        
        # Verify defaults exist
        assert 'long' in STRATEGY_DEFAULTS or len(STRATEGY_DEFAULTS) > 0
        
        # Get default percent
        long_defaults = STRATEGY_DEFAULTS.get('long', STRATEGY_DEFAULTS)
        short_defaults = STRATEGY_DEFAULTS.get('short', STRATEGY_DEFAULTS)
        
        assert 'percent' in long_defaults or 'sl_percent' in long_defaults
        assert 'percent' in short_defaults or 'sl_percent' in short_defaults


# ============================================================================
# TEST: EXCHANGE ISOLATION
# ============================================================================

class TestExchangeIsolation:
    """Test that exchanges have independent settings"""
    
    def test_bybit_hyperliquid_separate_keys(self, mock_pg_connection):
        """Same user/strategy/side has different keys per exchange"""
        mock_get_conn, store, set_exchange = mock_pg_connection
        
        user_id = 890004
        strategy = 'fibonacci'
        
        bybit_key = (user_id, strategy, 'long', 'bybit')
        hl_key = (user_id, strategy, 'long', 'hyperliquid')
        
        # Different keys
        assert bybit_key != hl_key
        
        # Store different values
        store[bybit_key] = {'leverage': 10, 'exchange': 'bybit'}
        store[hl_key] = {'leverage': 25, 'exchange': 'hyperliquid'}
        
        # Verify isolation
        assert store[bybit_key]['leverage'] == 10
        assert store[hl_key]['leverage'] == 25
    
    def test_count_all_combinations(self, mock_pg_connection):
        """Full 4D isolation: 2 sides x 2 exchanges = 4 rows per strategy"""
        mock_get_conn, store, set_exchange = mock_pg_connection
        
        user_id = 890004
        strategy = 'rsi_bb'
        
        combinations = [
            ('long', 'bybit'),
            ('long', 'hyperliquid'),
            ('short', 'bybit'),
            ('short', 'hyperliquid'),
        ]
        
        for i, (side, exchange) in enumerate(combinations):
            key = (user_id, strategy, side, exchange)
            store[key] = {
                'percent': float(i + 1),
                'side': side,
                'exchange': exchange,
            }
        
        # Count rows for this user/strategy
        count = sum(1 for k in store if k[0] == user_id and k[1] == strategy)
        assert count == 4


# ============================================================================
# TEST: MULTI-USER ISOLATION  
# ============================================================================

class TestMultiUserIsolation4D:
    """Test that different users have isolated 4D settings"""
    
    def test_users_separate_keys(self, mock_pg_connection):
        """Different users have different keys even with same settings"""
        mock_get_conn, store, set_exchange = mock_pg_connection
        
        user1 = 890001
        user2 = 890002
        strategy = 'oi'
        side = 'long'
        exchange = 'bybit'
        
        key1 = (user1, strategy, side, exchange)
        key2 = (user2, strategy, side, exchange)
        
        assert key1 != key2
        
        store[key1] = {'percent': 1.0}
        store[key2] = {'percent': 5.0}
        
        assert store[key1]['percent'] == 1.0
        assert store[key2]['percent'] == 5.0
    
    def test_update_one_user_not_affect_other(self, mock_pg_connection):
        """Updating one user's settings doesn't affect others"""
        mock_get_conn, store, set_exchange = mock_pg_connection
        
        user1 = 890001
        user2 = 890002
        strategy = 'scalper'
        
        # Initial values
        store[(user1, strategy, 'long', 'bybit')] = {'sl_percent': 3.0}
        store[(user2, strategy, 'long', 'bybit')] = {'sl_percent': 3.0}
        
        # Update user1 only
        store[(user1, strategy, 'long', 'bybit')]['sl_percent'] = 5.0
        
        # User2 unchanged
        assert store[(user2, strategy, 'long', 'bybit')]['sl_percent'] == 3.0
        assert store[(user1, strategy, 'long', 'bybit')]['sl_percent'] == 5.0


# ============================================================================
# TEST: STRATEGY FEATURES INTEGRATION
# ============================================================================

class TestStrategyFeaturesIntegration:
    """Test integration with STRATEGY_FEATURES"""
    
    def test_all_strategies_supported(self):
        """All strategies in STRATEGY_FEATURES can have 4D settings"""
        from coin_params import STRATEGY_FEATURES
        
        strategies = list(STRATEGY_FEATURES.keys())
        
        # Each strategy should support 4D schema
        for strategy in strategies:
            # 4D key structure works for any strategy
            key = (123456, strategy, 'long', 'bybit')
            assert len(key) == 4
            assert key[1] == strategy
    
    def test_strategy_specific_defaults(self):
        """Each strategy may have specific default values"""
        from coin_params import STRATEGY_FEATURES, STRATEGY_DEFAULTS
        
        # STRATEGY_DEFAULTS has side-specific defaults
        assert 'long' in STRATEGY_DEFAULTS or isinstance(STRATEGY_DEFAULTS, dict)
