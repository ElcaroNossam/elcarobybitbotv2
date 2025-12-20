import multiprocessing
import os

bind = "127.0.0.1:8000"

cpu_count = multiprocessing.cpu_count()
# МАКСИМАЛЬНАЯ НАГРУЗКА НА СЕРВЕР - используем все 8 CPU по максимуму (16GB RAM доступно)
if cpu_count <= 2:
    workers = 8
elif cpu_count <= 4:
    workers = 16
elif cpu_count <= 8:
    workers = 32  # Для 8 cores: 32 воркера (по 4 на ядро) - оптимально для I/O
else:
    workers = cpu_count * 4  # Для больших серверов

worker_class = "sync"
# worker_connections используется только для async workers (gevent, eventlet)
# Для sync workers не используется, но оставляем для совместимости
worker_connections = 10000  # Не используется для sync, но не повредит
timeout = 120
keepalive = 5
graceful_timeout = 60
max_requests = 2000  # Увеличено для меньших перезапусков (больше памяти доступно)
max_requests_jitter = 100  # Случайное отклонение для равномерной нагрузки
preload_app = True  # Загрузка приложения до форка workers для экономии памяти

loglevel = "info"

base_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(base_dir, "logs")

if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

errorlog = os.path.join(log_dir, "gunicorn_error.log")
accesslog = os.path.join(log_dir, "gunicorn_access.log")

