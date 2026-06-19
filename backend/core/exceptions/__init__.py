"""
Exceptions personnalisées pour l'API.
"""
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from django.http import JsonResponse


class BaseAPIException(APIException):
    """Exception de base pour l'API."""
    status_code = 400
    default_detail = 'Une erreur est survenue.'
    default_code = 'error'


class AuthenticationFailed(BaseAPIException):
    """Exception d'authentification."""
    status_code = 401
    default_detail = 'Authentification échouée.'
    default_code = 'authentication_failed'


class PermissionDenied(BaseAPIException):
    """Exception de permission."""
    status_code = 403
    default_detail = 'Permission refusée.'
    default_code = 'permission_denied'


class NotFound(BaseAPIException):
    """Exception de ressource non trouvée."""
    status_code = 404
    default_detail = 'Ressource non trouvée.'
    default_code = 'not_found'


class ValidationError(BaseAPIException):
    """Exception de validation."""
    status_code = 422
    default_detail = 'Erreur de validation.'
    default_code = 'validation_error'


class RateLimitExceeded(BaseAPIException):
    """Exception de limite de taux."""
    status_code = 429
    default_detail = 'Trop de requêtes.'
    default_code = 'rate_limit_exceeded'


class StockError(BaseAPIException):
    """Exception de stock."""
    status_code = 400
    default_detail = 'Erreur de stock.'
    default_code = 'stock_error'


class InsufficientStock(StockError):
    """Exception de stock insuffisant."""
    default_detail = 'Stock insuffisant pour cette opération.'
    default_code = 'insufficient_stock'


class ProductNotFound(NotFound):
    """Exception de produit non trouvé."""
    default_detail = 'Produit non trouvé.'
    default_code = 'product_not_found'


class SupplierNotFound(NotFound):
    """Exception de fournisseur non trouvé."""
    default_detail = 'Fournisseur non trouvé.'
    default_code = 'supplier_not_found'


class OrderError(BaseAPIException):
    """Exception de commande."""
    status_code = 400
    default_detail = 'Erreur de commande.'
    default_code = 'order_error'


class InventoryError(BaseAPIException):
    """Exception d'inventaire."""
    status_code = 400
    default_detail = 'Erreur d\'inventaire.'
    default_code = 'inventory_error'


def custom_exception_handler(exc, context):
    """Gestionnaire d'exceptions personnalisé."""
    response = exception_handler(exc, context)
    
    if response is not None:
        response.data = {
            'success': False,
            'message': str(exc.default_detail if hasattr(exc, 'default_detail') else exc),
            'errors': response.data if isinstance(response.data, dict) else {'detail': str(exc)},
            'code': exc.default_code if hasattr(exc, 'default_code') else 'error'
        }
    
    return response
