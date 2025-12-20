"""
Management command для синхронизации символов из Redis в БД.
Запускается автоматически при старте Daphne через ExecStartPre в systemd.
"""
import redis
from django.core.management.base import BaseCommand
from screener.models import Symbol


class Command(BaseCommand):
    help = 'Синхронизирует символы из Redis bar keys в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать что будет создано, но не создавать',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        try:
            redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            redis_client.ping()
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'❌ Не удалось подключиться к Redis: {e}'))
            return
        
        self.stdout.write('🔄 Сканирую Redis на наличие символов...')
        
        total_created = 0
        total_found = 0
        
        for market_type in ['spot', 'futures']:
            pattern = f"bars:{market_type}:*"
            symbols_found = set()
            
            # Сканируем все ключи
            cursor = 0
            while True:
                cursor, keys = redis_client.scan(cursor, match=pattern, count=1000)
                for key in keys:
                    # Формат: bars:spot:BTCUSDT:1234567890
                    parts = key.split(':')
                    if len(parts) >= 3:
                        symbol_name = parts[2]
                        symbols_found.add(symbol_name)
                if cursor == 0:
                    break
            
            self.stdout.write(f'  📊 {market_type}: найдено {len(symbols_found)} символов в Redis')
            total_found += len(symbols_found)
            
            if dry_run:
                # Показать что будет создано
                existing = set(Symbol.objects.filter(
                    market_type=market_type,
                    symbol__in=list(symbols_found)
                ).values_list('symbol', flat=True))
                new_symbols = symbols_found - existing
                if new_symbols:
                    self.stdout.write(f'    🆕 Будет создано: {len(new_symbols)} ({", ".join(list(new_symbols)[:5])}...)')
            else:
                # Создаем символы в БД
                created_count = 0
                for symbol_name in symbols_found:
                    obj, created = Symbol.objects.get_or_create(
                        symbol=symbol_name,
                        market_type=market_type,
                        defaults={'name': symbol_name}
                    )
                    if created:
                        created_count += 1
                
                total_created += created_count
                if created_count > 0:
                    self.stdout.write(self.style.SUCCESS(f'    ✅ Создано {created_count} новых символов'))
        
        # Итог
        if dry_run:
            self.stdout.write(self.style.WARNING(f'🔍 DRY RUN: найдено {total_found} символов в Redis'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✅ Синхронизация завершена: {total_created} новых символов создано'))
            
            # Показать общее количество в БД
            total_db = Symbol.objects.count()
            self.stdout.write(f'📊 Всего символов в БД: {total_db}')
