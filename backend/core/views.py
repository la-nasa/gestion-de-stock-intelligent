"""
Vues core.
"""
from django.http import JsonResponse
from django.db import connections
from django_redis import get_redis_connection


def health_check(request):
    """Vérification de l'état de santé de l'application."""
    status = {
        'status': 'healthy',
        'application': 'IUC Inventory System',
        'version': '1.0.0',
        'checks': {}
    }
    
    # Vérification base de données
    try:
        db_conn = connections['default']
        db_conn.cursor()
        status['checks']['database'] = 'connected'
    except Exception as e:
        status['checks']['database'] = f'error: {str(e)}'
        status['status'] = 'unhealthy'
    
    # Vérification Redis
    try:
        redis_conn = get_redis_connection('default')
        redis_conn.ping()
        status['checks']['redis'] = 'connected'
    except Exception as e:
        status['checks']['redis'] = f'error: {str(e)}'
        status['status'] = 'degraded'
    
    return JsonResponse(status)
