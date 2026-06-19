"""
Middleware de sécurité.
"""
import time
import logging
from django.conf import settings
from django.http import JsonResponse
from django.core.cache import cache

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware:
    """Ajoute des en-têtes de sécurité aux réponses."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # En-têtes de sécurité
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # Supprimer l'en-tête Server
        response['Server'] = ''
        
        return response


class RequestLoggingMiddleware:
    """Log les requêtes entrantes."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        # Logger les requêtes lentes
        if duration > 1.0:
            logger.warning(
                f"Requête lente: {request.method} {request.path} "
                f"({duration:.2f}s)"
            )
        
        return response


class RateLimitMiddleware:
    """Middleware de rate limiting."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Rate limiting basé sur l'IP
        if request.path.startswith('/api/'):
            ip = self.get_client_ip(request)
            key = f'rate_limit:{ip}:{request.path}'
            
            attempts = cache.get(key, 0)
            
            if attempts >= 100:  # 100 requêtes par minute
                return JsonResponse({
                    'success': False,
                    'message': 'Trop de requêtes. Veuillez réessayer plus tard.'
                }, status=429)
            
            cache.set(key, attempts + 1, 60)  # Expire après 60 secondes
        
        return self.get_response(request)
    
    def get_client_ip(self, request):
        """Récupère l'IP du client."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')
