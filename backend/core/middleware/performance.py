"""
Middleware de monitoring des performances.
"""
import time
import logging
from django.conf import settings

logger = logging.getLogger('performance')


class PerformanceMonitoringMiddleware:
    """Middleware qui log les requêtes lentes."""
    
    SLOW_THRESHOLD = 1.0  # secondes
    VERY_SLOW_THRESHOLD = 5.0  # secondes
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.slow_requests = 0
        self.total_requests = 0
    
    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        self.total_requests += 1
        
        # Logger les requêtes lentes
        if duration > self.VERY_SLOW_THRESHOLD:
            self.slow_requests += 1
            logger.error(
                f"TRÈS LENT: {request.method} {request.path} "
                f"({duration:.2f}s) - IP: {request.META.get('REMOTE_ADDR')}"
            )
        elif duration > self.SLOW_THRESHOLD:
            self.slow_requests += 1
            logger.warning(
                f"Lent: {request.method} {request.path} "
                f"({duration:.2f}s)"
            )
        
        # Ajouter l'en-tête de temps de réponse
        response['X-Response-Time'] = f'{duration:.3f}s'
        
        # Métriques
        if hasattr(request, 'user') and request.user.is_authenticated:
            logger.debug(
                f"OK: {request.method} {request.path} "
                f"({duration:.2f}s) - User: {request.user.email}"
            )
        
        return response


class QueryCountMiddleware:
    """Middleware qui compte les requêtes SQL."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        from django.db import connection
        
        response = self.get_response(request)
        
        if settings.DEBUG:
            query_count = len(connection.queries)
            query_time = sum(
                float(q.get('time', 0)) for q in connection.queries
            )
            
            if query_count > 50:
                logger.warning(
                    f"Nombreuses requêtes: {query_count} requêtes SQL "
                    f"({query_time:.3f}s) - {request.method} {request.path}"
                )
        
        return response