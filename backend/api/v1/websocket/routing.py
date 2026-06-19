"""
Configuration du routage WebSocket.
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/stock-updates/$', consumers.StockUpdateConsumer.as_asgi()),
]