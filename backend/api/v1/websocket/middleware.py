"""
Middleware d'authentification JWT pour WebSocket.
"""
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_str):
    """Récupère l'utilisateur à partir du token JWT."""
    try:
        token = AccessToken(token_str)
        user_id = token['user_id']
        user = User.objects.get(id=user_id, is_active=True)
        return user
    except (TokenError, InvalidToken, User.DoesNotExist, KeyError):
        return AnonymousUser()


class JWTAuthMiddleware:
    """
    Middleware qui authentifie l'utilisateur via JWT dans la query string.
    Format: ws://host/ws/path/?token=<jwt_token>
    """
    
    def __init__(self, inner):
        self.inner = inner
    
    async def __call__(self, scope, receive, send):
        # Récupérer le token de la query string
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]
        
        if token:
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()
        
        return await self.inner(scope, receive, send)