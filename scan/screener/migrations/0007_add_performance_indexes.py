# Generated migration for performance optimization
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('screener', '0006_screenersnapshot_change_1m_and_more'),
    ]

    operations = [
        # Индекс на market_type для быстрой фильтрации символов
        migrations.AddIndex(
            model_name='symbol',
            index=models.Index(fields=['market_type'], name='screener_sy_market__idx'),
        ),
        # Составной индекс для оптимизации запросов с фильтрацией по market_type и ts
        migrations.AddIndex(
            model_name='screenersnapshot',
            index=models.Index(fields=['symbol', '-ts'], name='screener_sn_symbol_ts_idx'),
        ),
    ]

