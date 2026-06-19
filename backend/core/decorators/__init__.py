"""
Décorateurs personnalisés.
"""
from functools import wraps
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied


def require_permission(permission_code: str):
    """Décorateur pour vérifier une permission spécifique."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'message': 'Authentification requise.'
                }, status=401)
            
            from services.rbac_service import RBACService
            if not RBACService.user_has_permission(request.user, permission_code):
                return JsonResponse({
                    'success': False,
                    'message': f"Permission '{permission_code}' requise."
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(*permission_codes: str):
    """Décorateur pour vérifier au moins une permission."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'message': 'Authentification requise.'
                }, status=401)
            
            from services.rbac_service import RBACService
            if not RBACService.user_has_any_permission(request.user, list(permission_codes)):
                return JsonResponse({
                    'success': False,
                    'message': 'Permissions insuffisantes.'
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_role(*roles: str):
    """Décorateur pour vérifier un rôle spécifique."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'message': 'Authentification requise.'
                }, status=401)
            
            if request.user.role not in roles:
                return JsonResponse({
                    'success': False,
                    'message': 'Rôle insuffisant.'
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
