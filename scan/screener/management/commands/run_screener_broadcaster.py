"""
Screener Broadcaster - читает snapshot'ы из БД и отправляет через WebSocket.

Новая архитектура:
    Binance → Workers → БД (ScreenerSnapshot) → Broadcaster → Channels → Browser

Broadcaster:
- Каждые 150ms читает свежие данные из ScreenerSnapshot
- Отправляет через channel_layer.group_send() в группы:
  * screener_spot
  * screener_futures
- НЕ знает про Binance, агрегацию, обработку данных
- Только читает БД и вещает в WebSocket
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db.models import F
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async

from screener.models import Symbol, ScreenerSnapshot

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Broadcas ter screener snapshots from DB to WebSocket consumers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=float,
            default=0.15,
            help='Broadcast interval in seconds (default: 0.15 = 150ms)',
        )

    def handle(self, *args, **options):
        """Entry point from Django management command"""
        interval = options['interval']
        self.stdout.write(
            self.style.SUCCESS(f'Starting screener broadcaster (interval={interval}s)...')
        )
        
        try:
            asyncio.run(self.broadcast_loop(interval))
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nBroadcaster stopped by user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Broadcaster crashed: {e}'))
            raise

    async def broadcast_loop(self, interval: float):
        """Main broadcast loop - sends snapshots to WebSocket groups"""
        channel_layer = get_channel_layer()
        
        if not channel_layer:
            logger.error("❌ Channel layer not configured! Check CHANNEL_LAYERS in settings.py")
            return
        
        logger.info(f"✅ Channel layer: {channel_layer.__class__.__name__}")
        logger.info(f"🚀 Broadcaster started, interval={interval}s")
        
        iteration = 0
        
        while True:
            iteration += 1
            start_time = asyncio.get_event_loop().time()
            
            try:
                # Отправляем spot и futures параллельно
                await asyncio.gather(
                    self.broadcast_market('spot', channel_layer),
                    self.broadcast_market('futures', channel_layer),
                    return_exceptions=True
                )
                
                # Логируем каждую 100-ю итерацию для мониторинга
                if iteration % 100 == 0:
                    logger.info(f"📡 Broadcaster iteration {iteration} completed")
                
            except Exception as e:
                logger.error(f"❌ Broadcast iteration {iteration} failed: {e}", exc_info=True)
            
            # Точная задержка с учётом времени выполнения
            elapsed = asyncio.get_event_loop().time() - start_time
            sleep_time = max(0, interval - elapsed)
            
            if elapsed > interval:
                logger.warning(f"⚠️  Broadcast took {elapsed:.3f}s (target={interval}s)")
            
            await asyncio.sleep(sleep_time)

    async def broadcast_market(self, market_type: str, channel_layer):
        """
        Читает snapshot из БД для одного market_type и отправляет в группу.
        
        Args:
            market_type: 'spot' или 'futures'
            channel_layer: Django Channels layer для group_send
        """
        try:
            # Профилирование
            t_start = asyncio.get_event_loop().time()
            
            # Получаем последний snapshot для каждого символа
            snapshots = await self.get_latest_snapshots(market_type)
            t_query = asyncio.get_event_loop().time()
            
            if not snapshots:
                # Это нормально в начале работы или если workers ещё не записали данные
                return
            
            # Форматируем данные в том же формате, что ждёт фронтенд
            formatted_data = []
            for snap in snapshots:
                formatted_data.append(self.format_snapshot_row(snap, market_type))
            t_format = asyncio.get_event_loop().time()
            
            # Отправляем в WebSocket группу
            group_name = f"screener_{market_type}"
            
            await channel_layer.group_send(
                group_name,
                {
                    'type': 'screener_data',
                    'data': formatted_data,
                    'market_type': market_type,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                }
            )
            t_send = asyncio.get_event_loop().time()
            
            # Логируем timing если медленно
            query_time = t_query - t_start
            format_time = t_format - t_query
            send_time = t_send - t_format
            total_time = t_send - t_start
            
            if total_time > 1.0:
                logger.warning(
                    f"⏱️  {market_type}: total={total_time:.2f}s "
                    f"(query={query_time:.2f}s, format={format_time:.2f}s, send={send_time:.2f}s)"
                )
            
        except Exception as e:
            logger.error(f"❌ Failed to broadcast {market_type}: {e}", exc_info=True)

    @sync_to_async
    def get_latest_snapshots(self, market_type: str) -> List[ScreenerSnapshot]:
        """
        Получает последний snapshot для каждого символа по market_type.
        
        Используем DISTINCT ON (PostgreSQL) для быстрого получения последней записи.
        Используем только необходимые поля для скорости.
        """
        # PostgreSQL DISTINCT ON - берёт первую запись для каждого symbol_id
        # Сортируем по symbol_id, -ts чтобы первая была самая свежая
        # Используем only() чтобы не загружать все 50+ полей
        snapshots = ScreenerSnapshot.objects.filter(
            symbol__market_type=market_type
        ).select_related('symbol').only(
            'symbol_id', 'ts', 'price',
            'vdelta_1m', 'vdelta_2m', 'vdelta_3m', 'vdelta_5m', 'vdelta_15m', 'vdelta_30m', 'vdelta_1h', 'vdelta_8h', 'vdelta_1d',
            'volume_1m', 'volume_2m', 'volume_3m', 'volume_5m', 'volume_15m', 'volume_30m', 'volume_1h', 'volume_8h', 'volume_1d',
            'change_1m', 'change_2m', 'change_3m', 'change_5m', 'change_15m', 'change_30m', 'change_1h', 'change_8h', 'change_1d',
            'volatility_1m', 'volatility_2m', 'volatility_3m', 'volatility_5m', 'volatility_15m', 'volatility_30m', 'volatility_1h',
            'ticks_1m', 'ticks_2m', 'ticks_3m', 'ticks_5m', 'ticks_15m', 'ticks_30m', 'ticks_1h',
            'open_interest', 'funding_rate',
            'oi_change_1m', 'oi_change_2m', 'oi_change_3m', 'oi_change_5m', 'oi_change_15m', 'oi_change_30m', 'oi_change_1h', 'oi_change_8h', 'oi_change_1d',
            'symbol__symbol', 'symbol__market_type'
        ).order_by(
            'symbol_id', '-ts'
        ).distinct('symbol_id')
        
        return list(snapshots)

    def format_snapshot_row(self, snap: ScreenerSnapshot, market_type: str) -> Dict:
        """
        Форматирует ScreenerSnapshot в формат для фронтенда.
        
        Важно: этот формат должен совпадать с тем, что сейчас ждёт screener.js
        """
        # Хелпер для конвертации Decimal в float
        def d(value):
            return float(value) if value is not None else 0.0
        
        row = {
            'symbol': snap.symbol.symbol,
            'market_type': market_type,
            'price': d(snap.price),
            'timestamp': snap.ts.isoformat(),
            
            # Price changes
            'change_1m': d(snap.change_1m),
            'change_2m': d(snap.change_2m),
            'change_3m': d(snap.change_3m),
            'change_5m': d(snap.change_5m),
            'change_15m': d(snap.change_15m),
            'change_30m': d(snap.change_30m),
            'change_1h': d(snap.change_1h),
            'change_8h': d(snap.change_8h),
            'change_1d': d(snap.change_1d),
            
            # Volumes
            'volume_1m': d(snap.volume_1m),
            'volume_2m': d(snap.volume_2m),
            'volume_3m': d(snap.volume_3m),
            'volume_5m': d(snap.volume_5m),
            'volume_15m': d(snap.volume_15m),
            'volume_30m': d(snap.volume_30m),
            'volume_1h': d(snap.volume_1h),
            'volume_8h': d(snap.volume_8h),
            'volume_1d': d(snap.volume_1d),
            
            # VDeltas
            'vdelta_1m': d(snap.vdelta_1m),
            'vdelta_2m': d(snap.vdelta_2m),
            'vdelta_3m': d(snap.vdelta_3m),
            'vdelta_5m': d(snap.vdelta_5m),
            'vdelta_15m': d(snap.vdelta_15m),
            'vdelta_30m': d(snap.vdelta_30m),
            'vdelta_1h': d(snap.vdelta_1h),
            'vdelta_8h': d(snap.vdelta_8h),
            'vdelta_1d': d(snap.vdelta_1d),
            
            # Volatility
            'volatility_1m': snap.volatility_1m,
            'volatility_2m': snap.volatility_2m,
            'volatility_3m': snap.volatility_3m,
            'volatility_5m': snap.volatility_5m,
            'volatility_15m': snap.volatility_15m,
            'volatility_30m': snap.volatility_30m,
            'volatility_1h': snap.volatility_1h,
            
            # Ticks
            'ticks_1m': snap.ticks_1m,
            'ticks_2m': snap.ticks_2m,
            'ticks_3m': snap.ticks_3m,
            'ticks_5m': snap.ticks_5m,
            'ticks_15m': snap.ticks_15m,
            'ticks_30m': snap.ticks_30m,
            'ticks_1h': snap.ticks_1h,
        }
        
        # Futures-specific поля
        if market_type == 'futures':
            row['open_interest'] = snap.open_interest
            row['funding_rate'] = snap.funding_rate
            
            row['oi_change_1m'] = d(snap.oi_change_1m)
            row['oi_change_2m'] = d(snap.oi_change_2m)
            row['oi_change_3m'] = d(snap.oi_change_3m)
            row['oi_change_5m'] = d(snap.oi_change_5m)
            row['oi_change_15m'] = d(snap.oi_change_15m)
            row['oi_change_30m'] = d(snap.oi_change_30m)
            row['oi_change_1h'] = d(snap.oi_change_1h)
            row['oi_change_8h'] = d(snap.oi_change_8h)
            row['oi_change_1d'] = d(snap.oi_change_1d)
        
        return row
