# Generated migration for database optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('screener', '0008_merge_20251207_0710'),
    ]

    operations = [
        # Добавляем составной индекс для быстрого поиска последнего snapshot
        migrations.AddIndex(
            model_name='screenersnapshot',
            index=models.Index(
                fields=['symbol', '-ts'],
                name='idx_snapshot_symbol_ts'
            ),
        ),
        
        # Добавляем индекс для market_type с INCLUDE (PostgreSQL specific)
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS idx_symbol_market_include 
                ON screener_symbol(market_type) 
                INCLUDE (symbol);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_symbol_market_include;",
            # Работает только на PostgreSQL
            state_operations=[],
        ),
        
        # Оптимизируем индекс для timestamp (без WHERE с NOW() - проблема IMMUTABLE)
        # Используем простой индекс без предиката для совместимости
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS idx_snapshot_symbol_ts_opt 
                ON screener_screenersnapshot(symbol_id, ts DESC);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_snapshot_symbol_ts_opt;",
            state_operations=[],
        ),
        
        # Индекс с INCLUDE для покрытия частых запросов (PostgreSQL specific)
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS idx_snapshot_covering 
                ON screener_screenersnapshot(symbol_id, ts DESC)
                INCLUDE (open_interest, price, funding_rate);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_snapshot_covering;",
            state_operations=[],
        ),
    ]
