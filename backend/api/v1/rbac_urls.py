"""
URLs pour la gestion RBAC.
"""
from django.urls import path
from api.v1.views.rbac_views import (
    RoleListView,
    RoleDetailView,
    RolePermissionsView,
    RolePermissionDetailView,
    PermissionListView,
    UserPermissionsView,
    UserRoleAssignView,
    UserRoleListView,
)

urlpatterns = [
    # Rôles
    path('rbac/roles/', RoleListView.as_view(), name='rbac-roles'),
    path('rbac/roles/<str:role_code>/', RoleDetailView.as_view(), name='rbac-role-detail'),
    
    # Permissions d'un rôle
    path('rbac/roles/<str:role_code>/permissions/', RolePermissionsView.as_view(), name='rbac-role-permissions'),
    path('rbac/roles/<str:role_code>/permissions/<str:permission_code>/', RolePermissionDetailView.as_view(), name='rbac-role-permission-detail'),
    
    # Permissions globales
    path('rbac/permissions/', PermissionListView.as_view(), name='rbac-permissions'),
    
    # Permissions utilisateur courant
    path('rbac/my-permissions/', UserPermissionsView.as_view(), name='rbac-my-permissions'),
    
    # Assignation de rôle
    path('rbac/assign-role/', UserRoleAssignView.as_view(), name='rbac-assign-role'),
    path('rbac/users/<str:role_code>/', UserRoleListView.as_view(), name='rbac-users-by-role'),
]
