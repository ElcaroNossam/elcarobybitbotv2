"""
Celery Task Queue for ElCaro Trading Platform
=============================================
Distributed task processing for 10K+ users

Task Types:
- Signal Processing: Process trading signals
- Position Monitoring: Monitor positions per user shard
- Trade Execution: Execute trades with rate limiting
- DCA Processing: Handle DCA orders
- ATR Trailing: Update trailing stops

Usage:
    # Start workers
    celery -A tasks.celery_app worker -Q signals -c 4 --loglevel=info
    celery -A tasks.celery_app worker -Q positions -c 8 --loglevel=info
    celery -A tasks.celery_app worker -Q trades -c 4 --loglevel=info
"""

from celery import Celery
import os

# Redis broker URL
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

app = Celery(
    'elcaro',
    broker=f"{REDIS_URL}/0",
    backend=f"{REDIS_URL}/1",
    include=[
        'tasks.signals',
        'tasks.positions', 
        'tasks.trades',
        'tasks.notifications'
    ]
)

# Configuration
app.conf.update(
    # Serialization
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    
    # Timezone
    timezone='UTC',
    enable_utc=True,
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_concurrency=8,
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks (memory leak prevention)
    
    # Task settings
    task_acks_late=True,  # Acknowledge after completion
    task_reject_on_worker_lost=True,  # Retry if worker dies
    task_time_limit=300,  # 5 min hard limit
    task_soft_time_limit=240,  # 4 min soft limit
    
    # Result settings
    result_expires=3600,  # Results expire after 1 hour
    
    # Task routing
    task_routes={
        'tasks.signals.*': {'queue': 'signals'},
        'tasks.positions.*': {'queue': 'positions'},
        'tasks.trades.*': {'queue': 'trades'},
        'tasks.notifications.*': {'queue': 'notifications'},
    },
    
    # Rate limits per task
    task_annotations={
        'tasks.trades.execute_trade': {
            'rate_limit': '10/s'  # Max 10 trades per second
        },
        'tasks.signals.process_signal': {
            'rate_limit': '100/s'  # Max 100 signals per second
        }
    },
    
    # Beat schedule (periodic tasks)
    beat_schedule={
        'monitor-all-positions': {
            'task': 'tasks.positions.monitor_all_positions',
            'schedule': 30.0,  # Every 30 seconds
        },
        'cleanup-expired-orders': {
            'task': 'tasks.trades.cleanup_expired_orders',
            'schedule': 300.0,  # Every 5 minutes
        },
        'sync-exchange-positions': {
            'task': 'tasks.positions.sync_exchange_positions',
            'schedule': 60.0,  # Every minute
        },
    }
)


if __name__ == '__main__':
    app.start()
