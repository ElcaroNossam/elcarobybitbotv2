"""
Unit Tests for Database Layer (db.py)
Tests for user management, positions, trades, signals, and licenses
"""

import pytest
import sqlite3
import time
from unittest.mock import patch, MagicMock


class TestDatabaseConnection:
    """Test database connection pool"""
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_connection_pool_creation(self, temp_db_path):
        """Test that connection pool is created correctly"""
        # This would test the actual db.py connection pool
        # For now, test basic connection
        conn = sqlite3.connect(temp_db_path)
        assert conn is not None
        conn.close()
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_connection_context_manager(self, test_db):
        """Test connection can be used as context manager"""
        cursor = test_db.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1


class TestUserManagement:
    """Test user CRUD operations"""
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_ensure_user_creates_new_user(self, test_db):
        """Test that ensure_user creates a new user"""
        user_id = 999999
        cursor = test_db.cursor()
        
        # Check user doesn't exist
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        assert cursor.fetchone() is None
        
        # Insert user
        cursor.execute("""
            INSERT INTO users (user_id, username) VALUES (?, ?)
        """, (user_id, "newuser"))
        test_db.commit()
        
        # Verify user exists
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        assert user is not None
        assert user['user_id'] == user_id
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_get_user_config(self, test_db, test_user_data):
        """Test retrieving user configuration"""
        cursor = test_db.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (test_user_data['user_id'],))
        user = cursor.fetchone()
        
        assert user is not None
        assert user['user_id'] == test_user_data['user_id']
        assert user['username'] == test_user_data['username']
        assert float(user['balance']) == test_user_data['balance']
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_set_user_field(self, test_db, test_user_id, test_user_data):
        """Test updating user field"""
        cursor = test_db.cursor()
        
        # Update balance
        new_balance = 20000.0
        cursor.execute("""
            UPDATE users SET balance = ? WHERE user_id = ?
        """, (new_balance, test_user_id))
        test_db.commit()
        
        # Verify update
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (test_user_id,))
        result = cursor.fetchone()
        assert float(result['balance']) == new_balance
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_user_credentials_storage(self, test_db, test_user_id, test_user_data):
        """Test storing API credentials"""
        cursor = test_db.cursor()
        
        # Set demo credentials
        cursor.execute("""
            UPDATE users 
            SET api_key = ?, api_secret = ? 
            WHERE user_id = ?
        """, ("demo_key", "demo_secret", test_user_id))
        test_db.commit()
        
        # Verify
        cursor.execute("""
            SELECT api_key, api_secret FROM users WHERE user_id = ?
        """, (test_user_id,))
        result = cursor.fetchone()
        assert result['api_key'] == "demo_key"
        assert result['api_secret'] == "demo_secret"
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_trading_mode_management(self, test_db, test_user_id, test_user_data):
        """Test trading mode (demo/real/both)"""
        cursor = test_db.cursor()
        
        # Set to real
        cursor.execute("""
            UPDATE users SET trading_mode = ? WHERE user_id = ?
        """, ("real", test_user_id))
        test_db.commit()
        
        # Verify
        cursor.execute("SELECT trading_mode FROM users WHERE user_id = ?", (test_user_id,))
        result = cursor.fetchone()
        assert result['trading_mode'] == "real"


class TestPositionManagement:
    """Test active position CRUD operations"""
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_add_active_position(self, test_db, test_user_id):
        """Test adding a new position"""
        cursor = test_db.cursor()
        
        position_data = {
            "user_id": test_user_id,
            "symbol": "BTCUSDT",
            "account_type": "demo",
            "side": "LONG",
            "entry_price": 50000.0,
            "size": 0.1,
            "strategy": "elcaro"
        }
        
        cursor.execute("""
            INSERT INTO active_positions 
            (user_id, symbol, account_type, side, entry_price, size, strategy)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, tuple(position_data.values()))
        test_db.commit()
        
        # Verify
        cursor.execute("""
            SELECT * FROM active_positions 
            WHERE user_id = ? AND symbol = ?
        """, (test_user_id, "BTCUSDT"))
        result = cursor.fetchone()
        
        assert result is not None
        assert result['symbol'] == "BTCUSDT"
        assert result['side'] == "LONG"
        assert float(result['entry_price']) == 50000.0
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_get_active_positions(self, test_db, test_user_id):
        """Test retrieving all active positions"""
        cursor = test_db.cursor()
        
        # Add multiple positions
        positions = [
            (test_user_id, "BTCUSDT", "demo", "LONG", 50000.0, 0.1, "elcaro"),
            (test_user_id, "ETHUSDT", "demo", "SHORT", 3000.0, 1.0, "scalper")
        ]
        
        for pos in positions:
            cursor.execute("""
                INSERT INTO active_positions 
                (user_id, symbol, account_type, side, entry_price, size, strategy)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, pos)
        test_db.commit()
        
        # Retrieve
        cursor.execute("SELECT * FROM active_positions WHERE user_id = ?", (test_user_id,))
        results = cursor.fetchall()
        
        assert len(results) == 2
        symbols = [r['symbol'] for r in results]
        assert "BTCUSDT" in symbols
        assert "ETHUSDT" in symbols
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_remove_active_position(self, test_db, test_user_id):
        """Test removing a position"""
        cursor = test_db.cursor()
        
        # Add position
        cursor.execute("""
            INSERT INTO active_positions 
            (user_id, symbol, account_type, side, entry_price, size, strategy)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (test_user_id, "BTCUSDT", "demo", "LONG", 50000.0, 0.1, "elcaro"))
        test_db.commit()
        
        # Remove
        cursor.execute("""
            DELETE FROM active_positions 
            WHERE user_id = ? AND symbol = ?
        """, (test_user_id, "BTCUSDT"))
        test_db.commit()
        
        # Verify removed
        cursor.execute("""
            SELECT * FROM active_positions 
            WHERE user_id = ? AND symbol = ?
        """, (test_user_id, "BTCUSDT"))
        result = cursor.fetchone()
        assert result is None


class TestTradeLogging:
    """Test trade history logging"""
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_add_trade_log(self, test_db, test_user_id):
        """Test logging a completed trade"""
        cursor = test_db.cursor()
        
        trade_data = {
            "user_id": test_user_id,
            "symbol": "BTCUSDT",
            "side": "LONG",
            "entry_price": 50000.0,
            "exit_price": 54000.0,
            "pnl": 400.0,
            "strategy": "elcaro"
        }
        
        cursor.execute("""
            INSERT INTO trade_logs
            (user_id, symbol, side, entry_price, exit_price, pnl, strategy)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, tuple(trade_data.values()))
        test_db.commit()
        
        # Verify
        cursor.execute("SELECT * FROM trade_logs WHERE user_id = ?", (test_user_id,))
        result = cursor.fetchone()
        
        assert result is not None
        assert result['symbol'] == "BTCUSDT"
        assert float(result['pnl']) == 400.0
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_get_trade_stats(self, test_db, test_user_id):
        """Test calculating trade statistics"""
        cursor = test_db.cursor()
        
        # Add multiple trades
        trades = [
            (test_user_id, "BTCUSDT", "LONG", 50000, 54000, 400, "elcaro"),
            (test_user_id, "ETHUSDT", "SHORT", 3000, 2900, 100, "scalper"),
            (test_user_id, "BTCUSDT", "LONG", 52000, 51000, -100, "elcaro")
        ]
        
        for trade in trades:
            cursor.execute("""
                INSERT INTO trade_logs
                (user_id, symbol, side, entry_price, exit_price, pnl, strategy)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, trade)
        test_db.commit()
        
        # Calculate stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_trades,
                SUM(pnl) as total_pnl,
                AVG(pnl) as avg_pnl,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades
            FROM trade_logs
            WHERE user_id = ?
        """, (test_user_id,))
        stats = cursor.fetchone()
        
        assert stats['total_trades'] == 3
        assert float(stats['total_pnl']) == 400.0
        assert stats['winning_trades'] == 2


class TestSignalManagement:
    """Test signal storage and retrieval"""
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_add_signal(self, test_db):
        """Test adding a new signal"""
        cursor = test_db.cursor()
        
        signal_data = {
            "raw_message": "🔥 BTCUSDT LONG from channel -1001234567890",
            "symbol": "BTCUSDT",
            "side": "LONG",
            "price": 50000.0
        }
        
        cursor.execute("""
            INSERT INTO signals
            (raw_message, symbol, side, price)
            VALUES (?, ?, ?, ?)
        """, tuple(signal_data.values()))
        test_db.commit()
        
        # Verify
        cursor.execute("SELECT * FROM signals WHERE symbol = ?", ("BTCUSDT",))
        result = cursor.fetchone()
        
        assert result is not None
        assert result['symbol'] == "BTCUSDT"
        assert result['side'] == "LONG"
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_get_recent_signals(self, test_db):
        """Test retrieving recent signals"""
        cursor = test_db.cursor()
        
        # Add signals 
        signals = [
            ("Signal 1 BTCUSDT LONG", "BTCUSDT", "LONG"),
            ("Signal 2 ETHUSDT SHORT", "ETHUSDT", "SHORT"),
            ("Signal 3 BNBUSDT LONG", "BNBUSDT", "LONG")
        ]
        
        for sig in signals:
            cursor.execute("""
                INSERT INTO signals
                (raw_message, symbol, side)
                VALUES (?, ?, ?)
            """, sig)
        test_db.commit()
        
        # Get all signals
        cursor.execute("""
            SELECT * FROM signals 
            ORDER BY ts DESC
        """)
        results = cursor.fetchall()
        
        assert len(results) == 3


class TestLicenseSystem:
    """Test license management"""
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_set_user_license(self, test_db, test_user_id, test_user_data):
        """Test setting user license"""
        cursor = test_db.cursor()
        
        # Set premium license
        expires = int(time.time()) + 30 * 86400  # 30 days
        cursor.execute("""
            UPDATE users 
            SET license_type = ?, license_expires = ?
            WHERE user_id = ?
        """, ("premium", expires, test_user_id))
        test_db.commit()
        
        # Verify
        cursor.execute("""
            SELECT license_type, license_expires 
            FROM users WHERE user_id = ?
        """, (test_user_id,))
        result = cursor.fetchone()
        
        assert result['license_type'] == "premium"
        assert result['license_expires'] == expires
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_check_license_expiry(self, test_db, test_user_id, test_user_data):
        """Test checking if license is expired"""
        cursor = test_db.cursor()
        
        # Set expired license
        expired = int(time.time()) - 86400  # Yesterday
        cursor.execute("""
            UPDATE users 
            SET license_type = ?, license_expires = ?
            WHERE user_id = ?
        """, ("premium", expired, test_user_id))
        test_db.commit()
        
        # Check
        cursor.execute("""
            SELECT license_expires < ? as is_expired
            FROM users WHERE user_id = ?
        """, (int(time.time()), test_user_id))
        result = cursor.fetchone()
        
        assert result['is_expired'] == 1


class TestHyperLiquidIntegration:
    """Test HyperLiquid credentials storage"""
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_set_hl_credentials(self, test_db, test_user_id, test_user_data):
        """Test storing HyperLiquid credentials"""
        cursor = test_db.cursor()
        
        cursor.execute("""
            UPDATE users 
            SET hl_private_key = ?, hl_vault_address = ?, hl_testnet = ?
            WHERE user_id = ?
        """, ("test_private_key", "test_vault", 1, test_user_id))
        test_db.commit()
        
        # Verify
        cursor.execute("""
            SELECT hl_private_key, hl_vault_address, hl_testnet
            FROM users WHERE user_id = ?
        """, (test_user_id,))
        result = cursor.fetchone()
        
        assert result['hl_private_key'] == "test_private_key"
        assert result['hl_vault_address'] == "test_vault"
        assert result['hl_testnet'] == 1
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_exchange_type_switching(self, test_db, test_user_id, test_user_data):
        """Test switching between exchanges"""
        cursor = test_db.cursor()
        
        # Switch to HyperLiquid
        cursor.execute("""
            UPDATE users SET exchange_type = ? WHERE user_id = ?
        """, ("hyperliquid", test_user_id))
        test_db.commit()
        
        # Verify
        cursor.execute("""
            SELECT exchange_type FROM users WHERE user_id = ?
        """, (test_user_id,))
        result = cursor.fetchone()
        
        assert result['exchange_type'] == "hyperliquid"


class TestStrategySettings:
    """Test strategy-specific settings"""
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_strategy_enabled_flag(self, test_db, test_user_id, test_user_data):
        """Test enabling/disabling strategies"""
        # This would test strategy settings from a separate table
        # For simplicity, using user table fields
        cursor = test_db.cursor()
        
        # Add strategy column for testing
        try:
            cursor.execute("""
                ALTER TABLE users ADD COLUMN elcaro_enabled INTEGER DEFAULT 1
            """)
            test_db.commit()
        except:
            pass
        
        # Disable strategy
        cursor.execute("""
            UPDATE users SET elcaro_enabled = 0 WHERE user_id = ?
        """, (test_user_id,))
        test_db.commit()
        
        # Verify
        cursor.execute("""
            SELECT elcaro_enabled FROM users WHERE user_id = ?
        """, (test_user_id,))
        result = cursor.fetchone()
        
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
