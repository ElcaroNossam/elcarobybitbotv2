"""
Management команда для очистки старых ликвидаций из БД.
Удаляет записи Liquidation старше указанного времени.

Usage:
    python manage.py cleanup_old_liquidations --hours 24
    python manage.py cleanup_old_liquidations --days 7
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from screener.models import Liquidation


class Command(BaseCommand):
    help = 'Delete old liquidations from database to save space'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Delete liquidations older than N hours (default: 24)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=None,
            help='Delete liquidations older than N days (overrides --hours)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        hours = options['hours']
        days = options['days']
        dry_run = options['dry_run']

        # Вычисляем cutoff время
        if days is not None:
            hours = days * 24
            period_str = f"{days} day(s)"
        else:
            period_str = f"{hours} hour(s)"

        cutoff = timezone.now() - timedelta(hours=hours)

        # Подсчитываем количество записей
        old_liquidations = Liquidation.objects.filter(timestamp__lt=cutoff)
        count = old_liquidations.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(f"✅ No liquidations older than {period_str}")
            )
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"🔍 DRY RUN: Would delete {count:,} liquidations older than {period_str} "
                    f"(before {cutoff})"
                )
            )
            
            # Показываем примеры записей
            samples = old_liquidations.select_related('symbol').order_by('timestamp')[:5]
            self.stdout.write("\nExamples of liquidations that would be deleted:")
            for liq in samples:
                self.stdout.write(
                    f"  - {liq.symbol.symbol} {liq.side} ${liq.notional_value} @ {liq.timestamp}"
                )
        else:
            self.stdout.write(f"🗑️  Deleting {count:,} liquidations older than {period_str}...")
            
            deleted_count, _ = old_liquidations.delete()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Deleted {deleted_count:,} liquidations (older than {cutoff})"
                )
            )
            
            # Показываем статистику после очистки
            remaining = Liquidation.objects.count()
            self.stdout.write(f"📊 Remaining liquidations in DB: {remaining:,}")
