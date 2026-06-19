"""
Configuration ASGI pour IUC Inventory System.
Supporte HTTP et WebSocket via Django Channels.
"""
import os
import django
from django.core.asgi import get_asgi_application

# Initialiser Django d'abord
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

# Importer après l'initialisation de Django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from api.v1.websocket.routing import websocket_urlpatterns
from api.v1.websocket.middleware import JWTAuthMiddleware

# Application HTTP Django
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    # HTTP requests
    'http': django_asgi_app,
    
    # WebSocket connections
    'websocket': AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            AuthMiddlewareStack(
                URLRouter(websocket_urlpatterns)
            )
        )
    ),
})