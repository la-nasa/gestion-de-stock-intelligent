"""Vues pour la gestion RBAC."""
from rest_framework import views, status
from apps.roles.models import Role, Permission
from apps.accounts.models import User
from api.v1.serializers.rbac_serializers import RoleSerializer, PermissionSerializer
from api.v1.permissions import IsManager, IsAdmin
from core.utils.response import success_response, error_response


class RoleListView(views.APIView):
    permission_classes = [IsManager]

    def get(self, request):
        roles = Role.objects.filter(is_active=True, is_deleted=False)
        serializer = RoleSerializer(roles, many=True)
        return success_response(data=serializer.data)


class PermissionListView(views.APIView):
    permission_classes = [IsManager]

    def get(self, request):
        permissions = Permission.objects.filter(is_active=True)
        serializer = PermissionSerializer(permissions, many=True)
        return success_response(data=serializer.data)


class UserRoleListView(views.APIView):
    permission_classes = [IsManager]

    def get(self, request, role_code):
        users = User.objects.filter(role=role_code, is_active=True)
        data = [{"id": str(u.id), "email": u.email, "full_name": u.get_full_name(), "role": u.role, "department": u.department.name if u.department else ""} for u in users]
        return success_response(data={"users": data, "count": len(data)})


class UserPermissionsView(views.APIView):
    def get(self, request):
        from services.rbac_service import RBACService
        perms = RBACService.get_user_permissions(request.user)
        return success_response(data={"permissions": sorted(list(perms)), "role": request.user.role, "count": len(perms)})
