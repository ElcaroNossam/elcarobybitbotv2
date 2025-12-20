"""
Management command to clean up all old data from the database.

Cleans:
1. Old ScreenerSnapshot records (older than 1 hour)
2. Old Liquidation records (older than 24 hours)
3. Unused Symbol records (no snapshots in last 7 days)
4. Redis bar data cleanup (handled automatically by TTL)

Usage:
    python manage.py cleanup_all
    python manage.py cleanup_all --dry-run
    
For cron (run every hour):
    0 * * * * cd /home/ubuntu/project/noetdat && /home/ubuntu/project/noetdat/venv/bin/python manage.py cleanup_all >> /var/log/noetdat/cleanup.log 2>&1
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import connection
from datetime import timedelta
import redis
import logging

from screener.models import ScreenerSnapshot, Liquidation, Symbol

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Clean up all old data from database (snapshots, liquidations, unused symbols)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting",
        )
        parser.add_argument(
            "--snapshot-hours",
            type=int,
            default=1,
            help="Delete snapshots older than N hours (default: 1)",
        )
        parser.add_argument(
            "--liquidation-hours",
            type=int,
            default=24,
            help="Delete liquidations older than N hours (default: 24)",
        )
        parser.add_argument(
            "--symbol-days",
            type=int,
            default=7,
            help="Delete symbols with no snapshots in N days (default: 7)",
        )
        parser.add_argument(
            "--vacuum",
            action="store_true",
            help="Run VACUUM ANALYZE after cleanup (PostgreSQL only)",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        snapshot_hours = options["snapshot_hours"]
        liquidation_hours = options["liquidation_hours"]
        symbol_days = options["symbol_days"]
        vacuum = options["vacuum"]

        now = timezone.now()
        total_deleted = 0
        
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"🧹 Database Cleanup Started at {now.strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write(f"{'='*60}\n")

        # 1. Clean old snapshots
        snapshot_cutoff = now - timedelta(hours=snapshot_hours)
        old_snapshots = ScreenerSnapshot.objects.filter(ts__lt=snapshot_cutoff)
        snapshot_count = old_snapshots.count()
        
        if snapshot_count > 0:
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f"📸 DRY RUN: Would delete {snapshot_count:,} snapshots older than {snapshot_hours}h"
                    )
                )
            else:
                # Batch delete for better performance
                deleted = 0
                batch_size = 10000
                while True:
                    batch_ids = list(
                        ScreenerSnapshot.objects.filter(ts__lt=snapshot_cutoff)
                        .values_list('id', flat=True)[:batch_size]
                    )
                    if not batch_ids:
                        break
                    ScreenerSnapshot.objects.filter(id__in=batch_ids).delete()
                    deleted += len(batch_ids)
                    self.stdout.write(f"  Deleted {deleted:,} snapshots...")
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"📸 Deleted {deleted:,} old snapshots (older than {snapshot_hours}h)"
                    )
                )
                total_deleted += deleted
        else:
            self.stdout.write(f"📸 No snapshots to clean (all fresh)")

        # 2. Clean old liquidations
        liquidation_cutoff = now - timedelta(hours=liquidation_hours)
        old_liquidations = Liquidation.objects.filter(timestamp__lt=liquidation_cutoff)
        liquidation_count = old_liquidations.count()
        
        if liquidation_count > 0:
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f"💥 DRY RUN: Would delete {liquidation_count:,} liquidations older than {liquidation_hours}h"
                    )
                )
            else:
                deleted, _ = old_liquidations.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"💥 Deleted {deleted:,} old liquidations (older than {liquidation_hours}h)"
                    )
                )
                total_deleted += deleted
        else:
            self.stdout.write(f"💥 No liquidations to clean (all fresh)")

        # 3. Clean unused symbols (no snapshots in N days)
        symbol_cutoff = now - timedelta(days=symbol_days)
        
        # Find symbols with no recent snapshots
        symbols_with_recent_snapshots = ScreenerSnapshot.objects.filter(
            ts__gte=symbol_cutoff
        ).values_list('symbol_id', flat=True).distinct()
        
        unused_symbols = Symbol.objects.exclude(id__in=symbols_with_recent_snapshots)
        unused_count = unused_symbols.count()
        
        if unused_count > 0:
            if dry_run:
                unused_list = list(unused_symbols.values_list('symbol', flat=True)[:10])
                self.stdout.write(
                    self.style.WARNING(
                        f"🪙 DRY RUN: Would delete {unused_count:,} unused symbols "
                        f"(no data in {symbol_days} days): {', '.join(unused_list)}..."
                    )
                )
            else:
                deleted, _ = unused_symbols.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"🪙 Deleted {deleted:,} unused symbols (no data in {symbol_days} days)"
                    )
                )
                total_deleted += deleted
        else:
            self.stdout.write(f"🪙 No unused symbols to clean")

        # 4. Clean Redis expired bars (info only - handled by TTL)
        try:
            r = redis.Redis(host='localhost', port=6379, db=0)
            bar_keys_spot = list(r.scan_iter(match='bars:spot:*', count=1000))
            bar_keys_futures = list(r.scan_iter(match='bars:futures:*', count=1000))
            self.stdout.write(
                f"📊 Redis bars: {len(bar_keys_spot):,} spot, {len(bar_keys_futures):,} futures "
                "(auto-cleaned by 25h TTL)"
            )
        except Exception as e:
            self.stdout.write(f"⚠️ Could not check Redis: {e}")

        # 5. Run VACUUM if requested
        if vacuum and not dry_run:
            self.stdout.write("\n🔧 Running VACUUM ANALYZE...")
            try:
                with connection.cursor() as cursor:
                    # Set autocommit for VACUUM
                    old_isolation_level = connection.connection.isolation_level
                    connection.connection.set_isolation_level(0)
                    cursor.execute("VACUUM ANALYZE screener_screenersnapshot;")
                    cursor.execute("VACUUM ANALYZE screener_liquidation;")
                    cursor.execute("VACUUM ANALYZE screener_symbol;")
                    connection.connection.set_isolation_level(old_isolation_level)
                self.stdout.write(self.style.SUCCESS("🔧 VACUUM ANALYZE completed"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"⚠️ VACUUM failed: {e}"))

        # Summary
        self.stdout.write(f"\n{'='*60}")
        if dry_run:
            self.stdout.write(self.style.WARNING("🔍 DRY RUN COMPLETED - No changes made"))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Cleanup completed! Total deleted: {total_deleted:,} records"
                )
            )
        self.stdout.write(f"{'='*60}\n")
