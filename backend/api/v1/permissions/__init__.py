"""
Permissions personnalisées pour l'API.
"""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Permission pour les administrateurs."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'


class IsManager(permissions.BasePermission):
    """Permission pour les gestionnaires."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['ADMIN', 'MANAGER']


class IsSupervisor(permissions.BasePermission):
    """Permission pour les superviseurs."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['ADMIN', 'MANAGER', 'SUPERVISOR']


class IsOperator(permissions.BasePermission):
    """Permission pour les opérateurs."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['ADMIN', 'MANAGER', 'SUPERVISOR', 'OPERATOR']


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission pour le propriétaire ou admin."""
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'ADMIN':
            return True
        return obj.user == request.user if hasattr(obj, 'user') else False


class IsDepartmentMember(permissions.BasePermission):
    """Permission pour les membres du même département."""
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'ADMIN':
            return True
        if hasattr(obj, 'department') and hasattr(request.user, 'department'):
            return obj.department == request.user.department
        return False


class IsCampusMember(permissions.BasePermission):
    """Permission pour les membres du même campus."""
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'ADMIN':
            return True
        if hasattr(obj, 'campus') and hasattr(request.user, 'campus'):
            return obj.campus == request.user.campus
        return False


class ReadOnly(permissions.BasePermission):
    """Permission lecture seule."""
    
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsWarehouseManager(permissions.BasePermission):
    """Permission pour le gestionnaire d'entrepôt."""
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'ADMIN':
            return True
        if hasattr(obj, 'warehouse') and hasattr(obj.warehouse, 'manager'):
            return obj.warehouse.manager == request.user
        if hasattr(obj, 'manager'):
            return obj.manager == request.user
        return False
