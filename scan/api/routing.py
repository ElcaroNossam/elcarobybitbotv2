"""
WebSocket URL routing for API.
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/screener/$', consumers.ScreenerConsumer.as_asgi()),
    re_path(r'^ws/liquidations/$', consumers.LiquidationConsumer.as_asgi()),
]

