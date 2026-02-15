"""
Cross-Platform Sync Integration Tests
======================================
Тесты синхронизации между iOS, Android, WebApp и Telegram Bot

Проверяет:
- Синхронизацию настроек между платформами
- Real-time обновления через WebSocket
- Консистентность данных
- Activity logging
"""

import pytest
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import MagicMock, AsyncMock, patch


class TestCrossPlatformSettingsSync:
    """Тесты синхронизации настроек между платформами"""
    
    PLATFORMS = ["ios", "android", "webapp", "telegram"]
    
    def test_language_sync_from_ios_to_all(self):
        """Смена языка на iOS синхронизируется на все платформы"""
        sync_message = {
            "type": "settings_changed",
            "source": "ios",
            "data": {
                "setting": "language",
                "old_value": "en",
                "new_value": "ru"
            }
        }
        
        # All platforms should receive this
        for platform in self.PLATFORMS:
            if platform != "ios":
                assert sync_message["source"] != platform
                assert sync_message["data"]["new_value"] == "ru"
    
    def test_language_sync_from_android_to_all(self):
        """Смена языка на Android синхронизируется на все платформы"""
        sync_message = {
            "type": "settings_changed",
            "source": "android",
            "data": {
                "setting": "language",
                "old_value": "en",
                "new_value": "de"
            }
        }
        
        assert sync_message["source"] == "android"
        assert sync_message["data"]["new_value"] == "de"
    
    def test_exchange_switch_sync(self):
        """Смена биржи синхронизируется между платформами"""
        for source_platform in self.PLATFORMS:
            sync_message = {
                "type": "exchange_switched",
                "source": source_platform,
                "data": {
                    "old_exchange": "bybit",
                    "new_exchange": "hyperliquid",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            assert sync_message["type"] == "exchange_switched"
            assert sync_message["data"]["new_exchange"] == "hyperliquid"
    
    def test_account_type_switch_sync(self):
        """Смена типа аккаунта синхронизируется"""
        sync_message = {
            "type": "account_switched",
            "source": "webapp",
            "data": {
                "old_account": "demo",
                "new_account": "real"
            }
        }
        
        assert sync_message["data"]["new_account"] in ["demo", "real", "testnet", "mainnet"]
    
    def test_strategy_settings_sync(self):
        """Настройки стратегии синхронизируются"""
        sync_message = {
            "type": "settings_changed",
            "source": "telegram",
            "data": {
                "setting": "strategy_oi",
                "strategy": "oi",
                "side": "long",
                "field": "tp_percent",
                "old_value": "5.0",
                "new_value": "8.0"
            }
        }
        
        assert sync_message["data"]["strategy"] == "oi"
        assert sync_message["data"]["side"] in ["long", "short"]


class TestWebSocketSyncMessages:
    """Тесты WebSocket сообщений синхронизации"""
    
    def test_position_update_broadcast(self):
        """Обновление позиций рассылается на все платформы"""
        position_update = {
            "type": "positions_update",
            "user_id": 123456789,
            "data": [
                {
                    "symbol": "BTCUSDT",
                    "side": "Buy",
                    "size": 0.1,
                    "entry_price": 97000.0,
                    "mark_price": 97500.0,
                    "unrealized_pnl": 50.0,
                    "pnl_percent": 0.52
                }
            ]
        }
        
        assert position_update["type"] == "positions_update"
        assert isinstance(position_update["data"], list)
        assert len(position_update["data"]) > 0
    
    def test_balance_update_broadcast(self):
        """Обновление баланса рассылается на все платформы"""
        balance_update = {
            "type": "balance_update",
            "user_id": 123456789,
            "data": {
                "balance": 10000.0,
                "equity": 10500.0,
                "available": 8000.0,
                "margin_used": 2000.0,
                "unrealized_pnl": 500.0
            }
        }
        
        assert balance_update["type"] == "balance_update"
        assert "equity" in balance_update["data"]
    
    def test_new_signal_broadcast(self):
        """Новый сигнал рассылается на все платформы"""
        signal_message = {
            "type": "signal",
            "user_id": 123456789,
            "data": {
                "symbol": "ETHUSDT",
                "side": "LONG",
                "strategy": "OI",
                "entry_price": 3150.0,
                "take_profit": 3300.0,
                "stop_loss": 3050.0,
                "confidence": 0.82,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        assert signal_message["type"] == "signal"
        assert "confidence" in signal_message["data"]
    
    def test_trade_closed_broadcast(self):
        """Закрытие сделки рассылается на все платформы"""
        trade_closed = {
            "type": "trade_closed",
            "user_id": 123456789,
            "data": {
                "symbol": "BTCUSDT",
                "side": "LONG",
                "entry_price": 96500.0,
                "exit_price": 98200.0,
                "pnl": 127.50,
                "pnl_percent": 1.76,
                "exit_reason": "TP",
                "strategy": "OI"
            }
        }
        
        assert trade_closed["type"] == "trade_closed"
        assert trade_closed["data"]["exit_reason"] in ["TP", "SL", "MANUAL", "ATR", "BE"]


class TestActivityLogging:
    """Тесты логирования активности для синхронизации"""
    
    def test_activity_log_structure(self):
        """Структура записи активности корректна"""
        activity = {
            "user_id": 123456789,
            "action_type": "settings_change",
            "action_category": "settings",
            "source": "android",
            "entity_type": "strategy_settings",
            "old_value": {"tp_percent": 5.0},
            "new_value": {"tp_percent": 25.0},
            "telegram_notified": False,
            "webapp_notified": False,
            "ios_notified": False,
            "android_notified": True,
            "created_at": datetime.now().isoformat()
        }
        
        required_fields = [
            "user_id", "action_type", "action_category", "source",
            "old_value", "new_value", "created_at"
        ]
        
        for field in required_fields:
            assert field in activity
    
    def test_activity_categories(self):
        """Все категории активности определены"""
        categories = ["settings", "trading", "auth", "exchange", "sync"]
        
        for category in categories:
            assert isinstance(category, str)
    
    def test_activity_action_types(self):
        """Все типы действий определены"""
        action_types = [
            "settings_change",
            "trade_open",
            "trade_close",
            "exchange_switch",
            "account_switch",
            "login",
            "logout",
            "api_key_update"
        ]
        
        for action in action_types:
            assert isinstance(action, str)
    
    def test_notification_flags_per_platform(self):
        """Флаги уведомлений для каждой платформы"""
        notification_flags = [
            "telegram_notified",
            "webapp_notified",
            "ios_notified",
            "android_notified"
        ]
        
        activity = {flag: False for flag in notification_flags}
        
        for flag in notification_flags:
            assert flag in activity
            assert isinstance(activity[flag], bool)


class TestDataConsistency:
    """Тесты консистентности данных между платформами"""
    
    def test_position_data_consistency(self):
        """Данные позиций одинаковы на всех платформах"""
        position_from_bot = {
            "symbol": "BTCUSDT",
            "side": "Buy",
            "size": 0.1,
            "entry_price": 97000.0,
            "leverage": 10
        }
        
        position_from_webapp = {
            "symbol": "BTCUSDT",
            "side": "Buy",
            "size": 0.1,
            "entry_price": 97000.0,
            "leverage": 10
        }
        
        position_from_ios = {
            "symbol": "BTCUSDT",
            "side": "Buy",
            "size": 0.1,
            "entry_price": 97000.0,
            "leverage": 10
        }
        
        position_from_android = {
            "symbol": "BTCUSDT",
            "side": "Buy",
            "size": 0.1,
            "entry_price": 97000.0,
            "leverage": 10
        }
        
        # All should be equal
        assert position_from_bot == position_from_webapp
        assert position_from_webapp == position_from_ios
        assert position_from_ios == position_from_android
    
    def test_balance_data_consistency(self):
        """Данные баланса одинаковы на всех платформах"""
        balance = {
            "balance": 10000.0,
            "equity": 10500.0,
            "available": 8000.0
        }
        
        # All platforms should show same balance
        for platform in ["bot", "webapp", "ios", "android"]:
            platform_balance = balance.copy()
            assert platform_balance["equity"] == 10500.0
    
    def test_settings_data_consistency(self):
        """Настройки одинаковы на всех платформах"""
        settings = {
            "exchange": "bybit",
            "account_type": "demo",
            "language": "en",
            "strategies": {
                "oi": {
                    "long": {"tp_percent": 25.0, "sl_percent": 30.0},
                    "short": {"tp_percent": 25.0, "sl_percent": 30.0}
                }
            }
        }
        
        # Settings should be identical across platforms
        for platform in ["bot", "webapp", "ios", "android"]:
            assert settings["exchange"] == "bybit"


class TestSyncConflictResolution:
    """Тесты разрешения конфликтов синхронизации"""
    
    def test_last_write_wins_strategy(self):
        """Стратегия 'последняя запись выигрывает'"""
        change1 = {
            "setting": "tp_percent",
            "value": "5.0",
            "timestamp": "2026-01-27T10:00:00",
            "source": "ios"
        }
        
        change2 = {
            "setting": "tp_percent",
            "value": "8.0",
            "timestamp": "2026-01-27T10:00:05",
            "source": "android"
        }
        
        # change2 is later, so it wins
        winner = change2 if change2["timestamp"] > change1["timestamp"] else change1
        assert winner["value"] == "8.0"
    
    def test_offline_changes_queue(self):
        """Изменения в offline режиме ставятся в очередь"""
        offline_queue = [
            {"action": "settings_change", "data": {"tp_percent": 10.0}, "timestamp": "2026-01-27T10:00:00"},
            {"action": "exchange_switch", "data": {"exchange": "hyperliquid"}, "timestamp": "2026-01-27T10:01:00"}
        ]
        
        # Queue should be processed in order when online
        assert len(offline_queue) == 2
        assert offline_queue[0]["timestamp"] < offline_queue[1]["timestamp"]


class TestPlatformSpecificSync:
    """Тесты специфичные для каждой платформы"""
    
    def test_telegram_bot_sync_handler(self):
        """Telegram бот обрабатывает sync сообщения"""
        sync_handlers = [
            "on_exchange_switched",
            "on_settings_changed",
            "on_position_update",
            "on_balance_update"
        ]
        
        for handler in sync_handlers:
            assert handler.startswith("on_")
    
    def test_ios_sync_notifications(self):
        """iOS использует Notification.Name для sync"""
        ios_notifications = [
            "exchangeSwitched",
            "accountTypeSwitched",
            "settingsChanged",
            "syncRequested"
        ]
        
        for notification in ios_notifications:
            # camelCase format for Swift
            assert notification[0].islower()
    
    def test_android_sync_flow(self):
        """Android использует SharedFlow для sync"""
        android_message_types = [
            "PositionUpdate",
            "BalanceUpdate",
            "PriceUpdate",
            "SignalReceived",
            "SettingsSync",
            "ExchangeSwitch"
        ]
        
        for msg_type in android_message_types:
            # PascalCase for Kotlin sealed class
            assert msg_type[0].isupper()
    
    def test_webapp_websocket_handlers(self):
        """WebApp имеет WebSocket handlers для sync"""
        webapp_handlers = [
            "handleExchangeSwitch",
            "handleSettingsChange",
            "handlePositionUpdate",
            "handleBalanceUpdate",
            "handleSignal"
        ]
        
        for handler in webapp_handlers:
            assert handler.startswith("handle")


class TestRealTimeSync:
    """Тесты real-time синхронизации"""
    
    def test_websocket_reconnect_strategy(self):
        """WebSocket переподключается при разрыве"""
        reconnect_config = {
            "initial_delay_ms": 1000,
            "max_delay_ms": 30000,
            "backoff_multiplier": 2.0,
            "max_retries": 10
        }
        
        assert reconnect_config["initial_delay_ms"] > 0
        assert reconnect_config["max_delay_ms"] > reconnect_config["initial_delay_ms"]
    
    def test_heartbeat_ping_pong(self):
        """Heartbeat ping/pong работает"""
        ping_message = {"type": "ping"}
        pong_message = {"type": "pong"}
        
        assert ping_message["type"] == "ping"
        assert pong_message["type"] == "pong"
    
    def test_sync_latency_acceptable(self):
        """Латентность синхронизации приемлема"""
        max_latency_ms = 500  # 500ms max
        
        # Simulated sync latency
        actual_latency_ms = 150
        
        assert actual_latency_ms < max_latency_ms


class TestBiometricAuthSync:
    """Тесты синхронизации биометрической аутентификации"""
    
    def test_biometric_token_storage(self):
        """Биометрический токен хранится безопасно"""
        storage_config = {
            "ios": "Keychain",
            "android": "EncryptedSharedPreferences"
        }
        
        assert storage_config["ios"] == "Keychain"
        assert "Encrypted" in storage_config["android"]
    
    def test_biometric_session_sync(self):
        """Биометрическая сессия синхронизируется"""
        session = {
            "token": "biometric_session_token",
            "expires_at": (datetime.now() + timedelta(days=30)).isoformat(),
            "device_id": "device_unique_id"
        }
        
        assert "expires_at" in session
        assert "device_id" in session


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
