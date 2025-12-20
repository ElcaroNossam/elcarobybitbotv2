import os
import django
import asyncio
import logging

# Set Django settings module BEFORE any Django imports
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Setup Django
django.setup()

# Now import Django and Channels components
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Import routing AFTER Django is fully configured
from api import routing

logger = logging.getLogger(__name__)

# ВАЖНО: Воркеры запускаются отдельным процессом через systemd (noetdat-workers.service)
# НЕ запускаем их здесь, чтобы избежать конфликтов и потери данных в памяти
logger.info("ASGI application initialized. Binance workers are managed by systemd service.")

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})


