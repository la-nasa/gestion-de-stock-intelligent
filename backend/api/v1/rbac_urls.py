from django.urls import path
from api.v1.views.rbac_views import RoleListView, PermissionListView, UserRoleListView, UserPermissionsView

urlpatterns = [
    path("rbac/roles/", RoleListView.as_view(), name="rbac-roles"),
    path("rbac/permissions/", PermissionListView.as_view(), name="rbac-permissions"),
    path("rbac/users/<str:role_code>/", UserRoleListView.as_view(), name="rbac-users-by-role"),
    path("rbac/my-permissions/", UserPermissionsView.as_view(), name="rbac-my-permissions"),
]
