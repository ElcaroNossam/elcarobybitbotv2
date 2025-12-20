"""
WebSocket consumers for real-time screener data.
Получает данные от Binance воркеров через Django Channels groups.
"""
import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.utils import timezone
from screener.utils import format_volume, format_vdelta
from screener.templatetags.formatting import format_price, format_ticks, format_volatility, format_oi_change
try:
    from autobahn.exception import Disconnected
except ImportError:
    # Fallback если autobahn не установлен
    Disconnected = ConnectionError

logger = logging.getLogger(__name__)


class ScreenerConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for screener data.
    Получает данные от Binance воркеров через Channels group.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        # Проверяем, есть ли данные в воркерах (но НЕ запускаем их — они работают через systemd)
        try:
            from api.binance_workers import _spot_data, _futures_data, _workers_started
            
            # Логируем состояние воркеров для диагностики
            spot_count = len(_spot_data) if _spot_data else 0
            futures_count = len(_futures_data) if _futures_data else 0
            logger.info(f"ScreenerConsumer connect: Workers status: _workers_started={_workers_started}, in-memory data: spot={spot_count}, futures={futures_count}")
            
            if spot_count == 0 and futures_count == 0:
                logger.warning(f"ScreenerConsumer: ⚠️ No data in memory yet. Client will receive data when workers populate it (check noetdat-workers.service).")
        except Exception as e:
            logger.debug(f"ScreenerConsumer: Could not check workers status: {e}")
        
        # Get market_type from query string
        query_string = self.scope.get('query_string', b'').decode('utf-8')
        market_type = 'spot'
        if 'market_type=' in query_string:
            for param in query_string.split('&'):
                if param.startswith('market_type='):
                    market_type = param.split('=')[1].strip()
                    break
        
        if market_type not in ['spot', 'futures']:
            market_type = 'spot'
        
        self.market_type = market_type
        self.group_name = f'screener_{market_type}'
        
        logger.info(f"[CONSUMER DEBUG] Connecting to group {self.group_name}, channel {self.channel_name}")
        
        # Join group
        try:
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            logger.info(f"[CONSUMER DEBUG] ✅ Successfully joined group {self.group_name}")
        except Exception as e:
            logger.error(f"[CONSUMER DEBUG] ❌ Failed to join group {self.group_name}: {e}", exc_info=True)
        
        await self.accept()
        
        logger.info(f"[CONSUMER DEBUG] WebSocket accepted and connected to {self.group_name}")
        
        # Send initial data
        await self.send_initial_data()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.debug(f"WebSocket disconnected: {self.group_name}, close_code={close_code}")
    
    async def receive(self, text_data):
        """Handle messages from WebSocket client."""
        try:
            data = json.loads(text_data)
            
            if data.get('type') == 'ping':
                # Respond to ping
                message = json.dumps({
                    'type': 'pong',
                    'timestamp': timezone.now().isoformat()
                })
                await self._safe_send(message)
        except json.JSONDecodeError:
            pass
        except Exception as e:
            logger.debug(f"ScreenerConsumer: Error handling receive: {e}")
    
    async def _safe_send(self, text_data: str):
        """Безопасная отправка данных через WebSocket с обработкой ошибок."""
        try:
            # Проверяем, что соединение еще активно
            if hasattr(self, 'scope') and self.scope.get('type') == 'websocket':
                await self.send(text_data=text_data)
                return True
            return False
        except (Disconnected, ConnectionError, OSError, RuntimeError):
            # Соединение закрыто или произошла ошибка сети - это нормально
            return False
        except Exception as e:
            # Проверяем все возможные варианты ошибок закрытого соединения
            error_msg = str(e).lower()
            error_type = type(e).__name__.lower()
            
            # Если это ошибка закрытого соединения - не логируем
            if any(keyword in error_msg or keyword in error_type for keyword in [
                'disconnected', 'closed', 'protocol', 'connection', 'websocket'
            ]):
                return False
            
            # Только реальные ошибки логируем
            logger.warning(f"ScreenerConsumer: Error sending WebSocket message: {e}")
            return False
    
    async def screener_data(self, event):
        """Receive screener data from group."""
        try:
            data = event.get('data', [])
            market_type = event.get('market_type', self.market_type)
            timestamp = event.get('timestamp', timezone.now().isoformat())
            
            # Лічильник для логування (кожні 100 повідомлень)
            if not hasattr(self, '_receive_count'):
                self._receive_count = 0
            self._receive_count += 1
            
            if self._receive_count % 100 == 0:
                logger.info(f"ScreenerConsumer: Sent {len(data)} rows for {market_type} (#{self._receive_count})")
            
            # Формируем JSON сообщение
            message = json.dumps({
                'type': 'screener_data',
                'data': data,
                'timestamp': timestamp,
                'market_type': market_type,
            })
            
            # Безопасная отправка
            await self._safe_send(message)
        except Exception as e:
            # Логируем только критические ошибки (не связанные с закрытием соединения)
            error_msg = str(e).lower()
            error_type = type(e).__name__.lower()
            
            # Если это ошибка закрытого соединения - не логируем как ошибку
            if any(keyword in error_msg or keyword in error_type for keyword in [
                'disconnected', 'closed', 'protocol', 'connection', 'websocket'
            ]):
                return  # Просто выходим, не логируем
            
            # Только реальные критические ошибки логируем
            logger.error(f"ScreenerConsumer: Error processing screener data: {e}", exc_info=True)
    
    async def liquidation_data(self, event):
        """Receive liquidation data from group."""
        try:
            data = event.get('data', {})
            market_type = event.get('market_type', 'futures')
            timestamp = event.get('timestamp', timezone.now().isoformat())
            
            # Формируем JSON сообщение
            message = json.dumps({
                'type': 'liquidation',
                'data': data,
                'timestamp': timestamp,
                'market_type': market_type,
            })
            
            # Безопасная отправка с обработкой ошибок
            sent = await self._safe_send(message)
            
            if sent:
                # Логируем первые 10 ликвидаций для диагностики
                if not hasattr(self, '_liquidation_sent_count'):
                    self._liquidation_sent_count = 0
                self._liquidation_sent_count += 1
                if self._liquidation_sent_count <= 10:
                    logger.info(f"ScreenerConsumer: ✅ Sent liquidation #{self._liquidation_sent_count} for {data.get('symbol', 'unknown')} to client")
                else:
                    logger.debug(f"ScreenerConsumer: Sent liquidation data for {data.get('symbol', 'unknown')} to client")
        except Exception as e:
            # Логируем только критические ошибки
            error_msg = str(e).lower()
            error_type = type(e).__name__.lower()
            
            # Если это ошибка закрытого соединения - не логируем как ошибку
            if any(keyword in error_msg or keyword in error_type for keyword in [
                'disconnected', 'closed', 'protocol', 'connection', 'websocket'
            ]):
                return  # Просто выходим, не логируем
            
            # Только реальные критические ошибки логируем
            logger.error(f"ScreenerConsumer: Error processing liquidation data: {e}", exc_info=True)
    
    def format_price(self, value):
        """Форматирует цену: округляет до целого."""
        if value is None:
            return ""
        try:
            return str(int(round(float(value))))
        except (ValueError, TypeError):
            return str(value)
    
    def format_change(self, value):
        """Форматирует изменение в процентах: 2 знака + '%'."""
        if value is None or value == "":
            return "0%"
        try:
            num_value = float(value)
            if num_value == 0:
                return "0%"
            return f"{num_value:.2f}%"
        except (ValueError, TypeError):
            return "0%"
    
    def format_volatility(self, value):
        """Форматирует волатильность в процентах: 2 знака + '%'."""
        if value is None or value == "":
            return "0%"
        try:
            num_value = float(value)
            if num_value == 0:
                return "0%"
            return f"{num_value:.2f}%"
        except (ValueError, TypeError):
            return "0%"
    
    def format_funding_rate(self, value):
        """Форматирует funding rate: умножает на 100, 4 знака + '%'."""
        if value is None or value == "":
            return "0.0000%"
        try:
            num_value = float(value) * 100  # Binance возвращает в долях, нужно умножить на 100
            return f"{num_value:.4f}%"
        except (ValueError, TypeError):
            return "0.0000%"
    
    def format_ticks(self, value):
        """Форматирует количество сделок: округляет до целого."""
        if value is None or value == "":
            return "0"
        try:
            return str(int(round(float(value))))
        except (ValueError, TypeError):
            return "0"
    
    def format_raw_dollar_precise(self, value):
        """Форматирует доллары с разными знаками в зависимости от величины."""
        if value is None or value == "":
            return "0$"
        try:
            num_value = float(value)
            if num_value == 0:
                return "0$"
            
            abs_value = abs(num_value)
            # Миллионы - без знаков после запятой
            if abs_value >= 1_000_000:
                formatted = f"{num_value:,.0f}$"
            # Тысячи - 1 знак после запятой
            elif abs_value >= 1_000:
                formatted = f"{num_value:,.1f}$"
            # Меньше тысячи - 2 знака после запятой
            else:
                formatted = f"{num_value:,.2f}$"
            
            return formatted
        except (ValueError, TypeError):
            return "0$"
    
    def format_volume(self, value, market_type):
        """Форматирует объем: использует format_raw_dollar_precise."""
        return self.format_raw_dollar_precise(value)
    
    def format_timestamp(self, ts_string):
        """Форматирует timestamp: HH:MM:SS.mmm."""
        if not ts_string or ts_string == "":
            return ""
        try:
            from datetime import datetime
            if isinstance(ts_string, str):
                ts_date = datetime.fromisoformat(ts_string.replace('Z', '+00:00'))
            else:
                return str(ts_string)
            
            hours = str(ts_date.hour).zfill(2)
            minutes = str(ts_date.minute).zfill(2)
            seconds = str(ts_date.second).zfill(2)
            milliseconds = str(ts_date.microsecond // 1000).zfill(3)
            return f"{hours}:{minutes}:{seconds}.{milliseconds}"
        except Exception:
            return str(ts_string)
    
    async def format_row_data(self, row: dict, market_type: str) -> dict:
        """Форматирует данные строки для отправки клиенту.
        
        Теперь форматирование выполняется на сервере для снижения нагрузки на браузер.
        """
        symbol = row.get('symbol', '')
        
        # Базовые данные
        price = row.get('price', 0)
        price_formatted = self.format_price(price)
        
        # Change данные - форматируем на сервере
        # ВАЖНО: используем реальные значения change_{tf} из row, а не fallback на change_24h
        # Это обеспечивает правильные значения для каждого таймфрейма
        change_data = {}
        change_formatted = {}
        for tf in ['1m', '3m', '5m', '15m', '30m', '1h', '4h', '8h', '1d']:
            change_tf = row.get(f'change_{tf}', 0)  # Fallback на 0, а не на change_24h!
            change_data[f'change_{tf}'] = change_tf
            change_formatted[f'change_{tf}_formatted'] = self.format_change(change_tf)
        
        # Volume данные - форматируем на сервере
        # ВАЖНО: каждый TF имеет свой volume по НОВОЙ МОДЕЛИ АГРЕГАЦИИ
        # Fallback на 0, а НЕ на volume_24h (это гарантирует правильность данных)
        volume_data = {}
        volume_formatted = {}
        for tf in ['1m', '3m', '5m', '15m', '30m', '1h', '4h', '8h', '1d']:
            volume_tf = row.get(f'volume_{tf}', 0)  # Fallback на 0!
            volume_data[f'volume_{tf}'] = volume_tf
            volume_formatted[f'volume_{tf}_formatted'] = self.format_volume(volume_tf, market_type)
        
        # Vdelta данные - форматируем на сервере
        vdelta_data = {}
        vdelta_formatted = {}
        for tf in ['1m', '3m', '5m', '15m', '30m', '1h', '4h', '8h', '1d']:
            vdelta_tf = row.get(f'vdelta_{tf}', 0)
            vdelta_data[f'vdelta_{tf}'] = vdelta_tf
            vdelta_formatted[f'vdelta_{tf}_formatted'] = self.format_raw_dollar_precise(vdelta_tf)
        
        # Ticks данные - форматируем на сервере
        ticks_1m = row.get('ticks_1m', 0)
        ticks_data = {}
        ticks_formatted = {}
        for tf in ['1m', '3m', '5m', '15m', '30m', '1h', '4h', '8h', '1d']:
            ticks_tf = row.get(f'ticks_{tf}', ticks_1m)
            ticks_data[f'ticks_{tf}'] = ticks_tf
            ticks_formatted[f'ticks_{tf}_formatted'] = self.format_ticks(ticks_tf)
        
        # Volatility данные - форматируем на сервере
        volatility_data = {}
        volatility_formatted = {}
        for tf in ['1m', '3m', '5m', '15m', '30m', '1h', '4h', '8h', '1d']:
            volatility_tf = row.get(f'volatility_{tf}', 0)
            volatility_data[f'volatility_{tf}'] = volatility_tf
            volatility_formatted[f'volatility_{tf}_formatted'] = self.format_volatility(volatility_tf)
        
        # OI Change данные - форматируем на сервере
        oi_change_data = {}
        oi_change_formatted = {}
        for tf in ['1m', '3m', '5m', '15m', '30m', '1h', '4h', '8h', '1d']:
            oi_change_tf = row.get(f'oi_change_{tf}', 0)
            oi_change_data[f'oi_change_{tf}'] = oi_change_tf
            oi_change_formatted[f'oi_change_{tf}_formatted'] = self.format_change(oi_change_tf)
        
        # Формируем итоговый объект
        row_timestamp = row.get('timestamp') or timezone.now().isoformat()
        formatted_row = {
            'symbol': symbol,
            'name': symbol,
            'price': price,
            'price_formatted': price_formatted,
            'ts': row_timestamp,
            'timestamp': row_timestamp,
            'timestamp_formatted': self.format_timestamp(row_timestamp),
            'market_type': market_type,
        }
        
        # Добавляем все данные (сырые и отформатированные)
        formatted_row.update(change_data)
        formatted_row.update(change_formatted)
        formatted_row.update(volume_data)
        formatted_row.update(volume_formatted)
        formatted_row.update(vdelta_data)
        formatted_row.update(vdelta_formatted)
        formatted_row.update(ticks_data)
        formatted_row.update(ticks_formatted)
        formatted_row.update(volatility_data)
        formatted_row.update(volatility_formatted)
        formatted_row.update(oi_change_data)
        formatted_row.update(oi_change_formatted)
        
        # Open Interest - форматируем на сервере
        open_interest = row.get('open_interest', 0)
        formatted_row['open_interest'] = open_interest
        formatted_row['open_interest_formatted'] = self.format_raw_dollar_precise(open_interest)
        
        if market_type == 'futures':
            funding_rate = row.get('funding_rate', 0)
            formatted_row['funding_rate'] = funding_rate
            formatted_row['funding_rate_formatted'] = self.format_funding_rate(funding_rate)
            formatted_row['mark_price'] = row.get('mark_price', 0)
        
        return formatted_row
    
    async def send_initial_data(self):
        """Send initial screener data (оптимизировано для multi-user)."""
        # Prefer reading latest aggregated snapshots from DB so clients get instant data
        try:
            from screener.models import ScreenerSnapshot, Symbol
            from asgiref.sync import sync_to_async
            
            # Wrap ALL DB access in sync_to_async to avoid "async context" errors
            @sync_to_async
            def get_initial_data_from_db():
                try:
                    # Postgres: use distinct on symbol_id to get latest snapshot per symbol efficiently
                    # Use select_related to avoid additional queries for symbol info
                    qs = ScreenerSnapshot.objects.filter(
                        symbol__market_type=self.market_type
                    ).select_related('symbol').order_by('symbol_id', '-ts').distinct('symbol_id')[:500]
                    
                    snapshots = list(qs)
                    
                    if not snapshots:
                        # Fallback: get latest snapshot per symbol using group logic (less efficient)
                        snaps = ScreenerSnapshot.objects.filter(
                            symbol__market_type=self.market_type
                        ).select_related('symbol').order_by('-ts')[:2000]
                        seen = set()
                        snapshots = []
                        for s in snaps:
                            sid = s.symbol_id
                            if sid in seen:
                                continue
                            seen.add(sid)
                            snapshots.append(s)
                            if len(snapshots) >= 500:
                                break
                    
                    # Build data here inside sync function to avoid async context errors
                    initial_data = []
                    for s in snapshots:
                        row = {
                            'symbol': s.symbol.symbol,
                            'price': float(s.price or 0),
                            'open_interest': float(s.open_interest or 0),
                            'funding_rate': float(s.funding_rate or 0),
                            'change_1m': float(s.change_1m or 0),
                            'change_2m': float(s.change_2m or 0),
                            'change_3m': float(s.change_3m or 0),
                            'change_5m': float(s.change_5m or 0),
                            'change_15m': float(s.change_15m or 0),
                            'change_30m': float(s.change_30m or 0),
                            'change_1h': float(s.change_1h or 0),
                            'change_8h': float(s.change_8h or 0),
                            'change_1d': float(s.change_1d or 0),
                        }

                        # volumes / vdelta / ticks / volatility
                        for tf in ['1m','3m','5m','15m','30m','1h','4h','8h','1d']:
                            row[f'vdelta_{tf}'] = float(getattr(s, f'vdelta_{tf}', 0) or 0)
                            row[f'volume_{tf}'] = float(getattr(s, f'volume_{tf}', 0) or 0)
                            row[f'change_{tf}'] = float(getattr(s, f'change_{tf}', 0) or 0)
                            # ticks and volatility fields may be absent for some TFs
                            row[f'ticks_{tf}'] = int(getattr(s, f'ticks_{tf}', 0) or 0)
                            row[f'volatility_{tf}'] = float(getattr(s, f'volatility_{tf}', 0) or 0)

                        row['timestamp'] = s.ts.isoformat()
                        row['ts'] = row['timestamp']  # Add ts alias for client compatibility
                        row['market_type'] = self.market_type
                        # DON'T format - keep raw data like workers do
                        initial_data.append(row)
                    
                    return initial_data
                except Exception as e:
                    logger.error(f"ScreenerConsumer: DB query failed: {e}", exc_info=True)
                    return []
            
            # Execute DB query asynchronously
            initial_data = await get_initial_data_from_db()
            
            # Execute DB query asynchronously
            initial_data = await get_initial_data_from_db()
            
            logger.debug(f"Got {len(initial_data)} rows from DB for {self.market_type}")
            
            if initial_data:
                logger.debug(f"Sending {len(initial_data)} symbols from DB for {self.market_type}")
            else:
                logger.warning(f"ScreenerConsumer: No initial DB data available for {self.market_type}, trying in-memory fallback...")
                # Fallback to in-memory data from workers
                try:
                    from api.binance_workers import _spot_data, _futures_data
                    data_store = _futures_data if self.market_type == 'futures' else _spot_data
                    
                    if data_store:
                        logger.debug(f"Found {len(data_store)} symbols in in-memory store for {self.market_type}")
                        for symbol, symbol_data in list(data_store.items())[:500]:
                            ticker = symbol_data.get('ticker', {})
                            price = ticker.get('price', 0) if ticker else 0
                            if not price or price == 0:
                                continue
                            
                            row = {'symbol': symbol, 'price': price, 'market_type': self.market_type}
                            # Add all timeframe data
                            for tf in ['1m','3m','5m','15m','30m','1h','4h','8h','1d']:
                                row[f'change_{tf}'] = symbol_data.get(f'change_{tf}', 0)
                                row[f'volume_{tf}'] = symbol_data.get(f'volume_{tf}', 0)
                                row[f'vdelta_{tf}'] = symbol_data.get(f'vdelta_{tf}', 0)
                                row[f'oi_change_{tf}'] = symbol_data.get(f'oi_change_{tf}', 0)
                            
                            for tf in ['1m','3m','5m','15m','30m','1h','4h','8h','1d']:
                                row[f'ticks_{tf}'] = symbol_data.get(f'ticks_{tf}', 0)
                                row[f'volatility_{tf}'] = symbol_data.get(f'volatility_{tf}', 0)
                            
                            row['open_interest'] = symbol_data.get('open_interest', 0)
                            row['funding_rate'] = symbol_data.get('funding_rate', 0)
                            row['timestamp'] = timezone.now().isoformat()
                            row['ts'] = row['timestamp']
                            
                            # Don't format in initial_data - keep raw like workers do
                            initial_data.append(row)
                        
                        if initial_data:
                            logger.debug(f"Sending {len(initial_data)} symbols from in-memory for {self.market_type}")
                    else:
                        logger.warning(f"ScreenerConsumer: In-memory store is empty for {self.market_type}")
                except Exception as mem_error:
                    logger.error(f"ScreenerConsumer: In-memory fallback failed: {mem_error}")

            message = json.dumps({
                'type': 'screener_data',
                'data': initial_data,
                'timestamp': timezone.now().isoformat(),
                'market_type': self.market_type,
            })
            await self._safe_send(message)
            
            if not initial_data:
                logger.error(f"ScreenerConsumer: Sent 0 symbols to client for {self.market_type}!")
        except Exception as e:
            logger.error(f"ScreenerConsumer: DB initial data failed: {e}")
            # Fallback: original in-memory behavior (workers will still send group messages)
            try:
                from api.binance_workers import _spot_data, _futures_data
                data_store = _futures_data if self.market_type == 'futures' else _spot_data
                initial_data = []
                if data_store:
                    for symbol, symbol_data in list(data_store.items())[:500]:
                        ticker = symbol_data.get('ticker', {})
                        klines = symbol_data.get('kline', {})
                        agg_trade = symbol_data.get('aggTrade', {})
                        price = ticker.get('price', 0) if ticker else 0
                        if not price and klines:
                            for interval in ['1m', '5m', '15m', '1h']:
                                if interval in klines:
                                    price = klines[interval].get('close', 0)
                                    if price > 0:
                                        break
                        if not price:
                            continue
                        row = {'symbol': symbol, 'price': price, 'change_24h': ticker.get('change', 0) if ticker else 0, 'ticks_1m': agg_trade.get('ticks', 0) if agg_trade else 0}
                        # НОВАЯ МОДЕЛЬ: каждый TF имеет свой volume (НЕ используем volume_24h как fallback!)
                        for interval in ['1m','2m','3m','5m','15m','30m','1h','8h','1d']:
                            if interval in klines:
                                kline = klines[interval]
                                open_price = kline.get('open', 0)
                                close_price = kline.get('close', 0)
                                if open_price > 0:
                                    row[f'change_{interval}'] = ((close_price - open_price) / open_price) * 100
                                    row[f'volatility_{interval}'] = ((kline.get('high',0) - kline.get('low',0)) / open_price) * 100
                                else:
                                    row[f'change_{interval}'] = 0.0
                                    row[f'volatility_{interval}'] = 0.0
                                row[f'volume_{interval}'] = kline.get('quote_volume', 0)
                                row[f'ticks_{interval}'] = kline.get('trades', 0)
                            else:
                                # Fallback если данных еще нет
                                row[f'change_{interval}'] = 0.0
                                row[f'volatility_{interval}'] = 0.0
                                row[f'volume_{interval}'] = 0.0  # НЕ volume_24h!
                                row[f'ticks_{interval}'] = 0
                        if agg_trade and 'windows' in agg_trade:
                            windows = agg_trade['windows']
                            for interval in ['1m','2m','3m','5m','15m','30m','1h','8h','1d']:
                                row[f'vdelta_{interval}'] = sum(v for _, v in windows.get(interval, []))
                        else:
                            for interval in ['1m','2m','3m','5m','15m','30m','1h','8h','1d']:
                                row[f'vdelta_{interval}'] = 0
                        row['timestamp'] = agg_trade.get('last_update', timezone.now().isoformat()) if agg_trade else timezone.now().isoformat()
                        formatted_row = await self.format_row_data(row, self.market_type)
                        initial_data.append(formatted_row)
                message = json.dumps({'type':'screener_data','data':initial_data,'timestamp':timezone.now().isoformat(),'market_type':self.market_type})
                await self._safe_send(message)
            except Exception:
                try:
                    await self._safe_send(json.dumps({'type': 'screener_data', 'data': [], 'timestamp': timezone.now().isoformat(), 'market_type': self.market_type}))
                except:
                    pass


class LiquidationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer для real-time потока ликвидаций.
    Подписывается на Redis PubSub канал 'liquidations'.
    Поддерживает фильтрацию по symbol, market_type, min_notional.
    """
    
    async def connect(self):
        """Подключение клиента к WebSocket."""
        self.filters = {
            'symbols': [],       # Пустой список = все символы
            'market_type': None, # None = все типы (spot/futures)
            'min_notional': 0    # Минимальный размер ликвидации в USDT
        }
        
        # Подключаемся к Channels group для legacy поддержки
        await self.channel_layer.group_add("liquidations", self.channel_name)
        await self.accept()
        
        logger.info(f"[Liquidations WS] Client connected: {self.channel_name}")
        
        # Запускаем подписку на Redis PubSub в фоне
        asyncio.create_task(self._subscribe_to_redis())
    
    async def disconnect(self, close_code):
        """Отключение клиента."""
        # Отписываемся от group
        await self.channel_layer.group_discard("liquidations", self.channel_name)
        
        # Останавливаем подписку Redis
        if hasattr(self, '_redis_task'):
            self._redis_task.cancel()
        
        logger.info(f"[Liquidations WS] Client disconnected: {self.channel_name}")
    
    async def receive(self, text_data):
        """Получение сообщения от клиента (настройка фильтров)."""
        try:
            data = json.loads(text_data)
            
            if data.get('type') == 'set_filters':
                # Клиент отправляет фильтры: {"type": "set_filters", "filters": {...}}
                self.filters.update(data.get('filters', {}))
                logger.info(f"[Liquidations WS] Filters updated for {self.channel_name}: {self.filters}")
                
                await self.send(text_data=json.dumps({
                    'type': 'filters_updated',
                    'filters': self.filters
                }))
                
            elif data.get('type') == 'ping':
                # Keep-alive ping
                await self.send(text_data=json.dumps({'type': 'pong'}))
                
        except json.JSONDecodeError:
            logger.error(f"[Liquidations WS] Invalid JSON from client: {text_data}")
        except Exception as e:
            logger.error(f"[Liquidations WS] Error in receive: {e}", exc_info=True)
    
    async def _subscribe_to_redis(self):
        """Подписка на Redis PubSub канал 'liquidations'."""
        import redis.asyncio as aioredis
        
        try:
            # Подключаемся к Redis
            redis_client = await aioredis.from_url('redis://localhost:6379/0')
            pubsub = redis_client.pubsub()
            
            # Подписываемся на канал
            await pubsub.subscribe('liquidations')
            logger.info(f"[Liquidations WS] Subscribed to Redis PubSub 'liquidations'")
            
            # Слушаем сообщения
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        # Парсим данные ликвидации
                        liquidation = json.loads(message['data'])
                        
                        # Применяем фильтры
                        if self._matches_filters(liquidation):
                            await self.send(text_data=json.dumps({
                                'type': 'liquidation',
                                'data': liquidation
                            }))
                            
                    except json.JSONDecodeError:
                        logger.error(f"[Liquidations WS] Invalid JSON from Redis: {message['data']}")
                    except Exception as e:
                        logger.error(f"[Liquidations WS] Error processing message: {e}", exc_info=True)
                        
        except asyncio.CancelledError:
            logger.info(f"[Liquidations WS] Redis subscription cancelled for {self.channel_name}")
            await pubsub.unsubscribe('liquidations')
            await redis_client.close()
        except Exception as e:
            logger.error(f"[Liquidations WS] Redis subscription error: {e}", exc_info=True)
    
    def _matches_filters(self, liquidation: dict) -> bool:
        """Проверяет, соответствует ли ликвидация фильтрам клиента."""
        # Фильтр по символам
        if self.filters['symbols'] and liquidation['symbol'] not in self.filters['symbols']:
            return False
        
        # Фильтр по market_type
        if self.filters['market_type'] and liquidation.get('market_type') != self.filters['market_type']:
            return False
        
        # Фильтр по минимальному размеру
        if liquidation.get('notional', 0) < self.filters['min_notional']:
            return False
        
        return True
    
    async def liquidation_data(self, event):
        """Обработчик события liquidation_data от Channels group (legacy)."""
        # Legacy метод для обратной совместимости с Channels
        # Основной метод = Redis PubSub в _subscribe_to_redis()
        try:
            liquidation = event['data']
            
            if self._matches_filters(liquidation):
                await self.send(text_data=json.dumps({
                    'type': 'liquidation',
                    'data': liquidation,
                    'timestamp': event.get('timestamp')
                }))
        except Exception as e:
            logger.error(f"[Liquidations WS] Error in liquidation_data: {e}", exc_info=True)
