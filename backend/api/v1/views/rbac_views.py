"""
Vues pour la gestion RBAC.
"""
from rest_framework import views, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.roles.models import Role, Permission, RolePermission
from apps.accounts.models import User
from api.v1.serializers.rbac_serializers import (
    RoleSerializer,
    RoleCreateSerializer,
    PermissionSerializer,
    PermissionListSerializer,
    RolePermissionSerializer,
    AssignRoleSerializer,
    BulkPermissionAssignSerializer,
    UserPermissionsSerializer,
)
from api.v1.permissions import IsAdmin, IsManager
from core.utils.response import success_response, error_response
from services.rbac_service import RBACService


class RoleListView(views.APIView):
    """Liste et création des rôles."""
    
    permission_classes = [IsManager]
    
    @swagger_auto_schema(
        operation_description="Liste tous les rôles",
        responses={200: RoleSerializer(many=True)}
    )
    def get(self, request):
        roles = RBACService.get_all_roles()
        serializer = RoleSerializer(roles, many=True)
        return success_response(data=serializer.data)
    
    @swagger_auto_schema(
        operation_description="Crée un nouveau rôle",
        request_body=RoleCreateSerializer,
        responses={201: RoleSerializer()}
    )
    def post(self, request):
        if not request.user.role == 'ADMIN':
            return error_response(
                message="Seuls les administrateurs peuvent créer des rôles.",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        serializer = RoleCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return error_response(
                message="Erreur de validation",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        role = serializer.save()
        output_serializer = RoleSerializer(role)
        
        return success_response(
            data=output_serializer.data,
            message="Rôle créé avec succès",
            status_code=status.HTTP_201_CREATED
        )


class RoleDetailView(views.APIView):
    """Détail, mise à jour et suppression d'un rôle."""
    
    permission_classes = [IsManager]
    
    def get_role(self, role_code):
        try:
            return Role.objects.get(code=role_code, is_deleted=False)
        except Role.DoesNotExist:
            return None
    
    @swagger_auto_schema(operation_description="Détail d'un rôle")
    def get(self, request, role_code):
        role = self.get_role(role_code)
        if not role:
            return error_response(
                message="Rôle introuvable.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = RoleSerializer(role)
        return success_response(data=serializer.data)
    
    @swagger_auto_schema(
        operation_description="Met à jour un rôle",
        request_body=RoleSerializer
    )
    def patch(self, request, role_code):
        if request.user.role != 'ADMIN':
            return error_response(
                message="Seuls les administrateurs peuvent modifier les rôles.",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        role = self.get_role(role_code)
        if not role:
            return error_response(
                message="Rôle introuvable.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        if role.is_system:
            return error_response(
                message="Impossible de modifier un rôle système.",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        serializer = RoleSerializer(role, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(
                message="Erreur de validation",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        return success_response(
            data=serializer.data,
            message="Rôle mis à jour"
        )
    
    @swagger_auto_schema(operation_description="Supprime un rôle")
    def delete(self, request, role_code):
        if request.user.role != 'ADMIN':
            return error_response(
                message="Seuls les administrateurs peuvent supprimer les rôles.",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        role = self.get_role(role_code)
        if not role:
            return error_response(
                message="Rôle introuvable.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        if role.is_system:
            return error_response(
                message="Impossible de supprimer un rôle système.",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        RBACService.delete_role(role)
        return success_response(message="Rôle supprimé")


class RolePermissionsView(views.APIView):
    """Gestion des permissions d'un rôle."""
    
    permission_classes = [IsManager]
    
    @swagger_auto_schema(operation_description="Liste les permissions d'un rôle")
    def get(self, request, role_code):
        try:
            role = Role.objects.get(code=role_code, is_deleted=False)
        except Role.DoesNotExist:
            return error_response(
                message="Rôle introuvable.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        permissions = RolePermission.objects.filter(role=role)
        serializer = RolePermissionSerializer(permissions, many=True)
        return success_response(data=serializer.data)
    
    @swagger_auto_schema(
        operation_description="Ajoute une permission au rôle",
        request_body=RolePermissionSerializer
    )
    def post(self, request, role_code):
        if request.user.role != 'ADMIN':
            return error_response(
                message="Seuls les administrateurs peuvent modifier les permissions.",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        try:
            role = Role.objects.get(code=role_code, is_deleted=False)
        except Role.DoesNotExist:
            return error_response(
                message="Rôle introuvable.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = RolePermissionSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Erreur de validation",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        permission = Permission.objects.get(
            code=serializer.validated_data['permission_code']
        )
        
        try:
            rp = RBACService.assign_permission_to_role(
                role, permission, granted_by=request.user
            )
            output = RolePermissionSerializer(rp)
            return success_response(
                data=output.data,
                message="Permission assignée",
                status_code=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return error_response(message=str(e), status_code=status.HTTP_409_CONFLICT)
    
    @swagger_auto_schema(
        operation_description="Assigne plusieurs permissions au rôle",
        request_body=BulkPermissionAssignSerializer
    )
    def put(self, request, role_code):
        if request.user.role != 'ADMIN':
            return error_response(
                message="Seuls les administrateurs peuvent modifier les permissions.",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        try:
            role = Role.objects.get(code=role_code, is_deleted=False)
        except Role.DoesNotExist:
            return error_response(
                message="Rôle introuvable.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = BulkPermissionAssignSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Erreur de validation",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        permissions = Permission.objects.filter(
            code__in=serializer.validated_data['permission_codes']
        )
        
        count = RBACService.assign_permissions_to_role_bulk(
            role, list(permissions), granted_by=request.user
        )
        
        return success_response(
            message=f"{count} permission(s) assignée(s)"
        )


class RolePermissionDetailView(views.APIView):
    """Suppression d'une permission d'un rôle."""
    
    permission_classes = [IsAdmin]
    
    @swagger_auto_schema(operation_description="Révoque une permission d'un rôle")
    def delete(self, request, role_code, permission_code):
        try:
            role = Role.objects.get(code=role_code, is_deleted=False)
        except Role.DoesNotExist:
            return error_response(
                message="Rôle introuvable.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        try:
            permission = Permission.objects.get(code=permission_code)
        except Permission.DoesNotExist:
            return error_response(
                message="Permission introuvable.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        success = RBACService.revoke_permission_from_role(role, permission)
        if success:
            return success_response(message="Permission révoquée")
        return error_response(
            message="Permission non trouvée pour ce rôle.",
            status_code=status.HTTP_404_NOT_FOUND
        )


class PermissionListView(views.APIView):
    """Liste des permissions disponibles."""
    
    permission_classes = [IsManager]
    
    @swagger_auto_schema(operation_description="Liste toutes les permissions")
    def get(self, request):
        module = request.query_params.get('module', None)
        
        if module:
            permissions = RBACService.get_permissions_by_module(module)
        else:
            permissions = RBACService.get_all_permissions()
        
        serializer = PermissionSerializer(permissions, many=True)
        return success_response(data=serializer.data)


class UserPermissionsView(views.APIView):
    """Permissions de l'utilisateur connecté."""
    
    def get(self, request):
        permissions = RBACService.get_user_permissions(request.user)
        
        data = {
            'user': request.user,
            'role': request.user.role,
            'permissions': sorted(list(permissions)),
            'total': len(permissions)
        }
        
        serializer = UserPermissionsSerializer(data)
        return success_response(data=serializer.data)


class UserRoleAssignView(views.APIView):
    """Assignation de rôle à un utilisateur."""
    
    permission_classes = [IsAdmin]
    
    @swagger_auto_schema(
        operation_description="Assigne un rôle à un utilisateur",
        request_body=AssignRoleSerializer
    )
    def post(self, request):
        serializer = AssignRoleSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message="Erreur de validation",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        user = serializer.validated_data['user_id']
        role = serializer.validated_data['role_code']
        
        RBACService.assign_role_to_user(user, role.code)
        
        return success_response(
            message=f"Rôle '{role.name}' assigné à {user.get_full_name()}"
        )


class UserRoleListView(views.APIView):
    """Liste des utilisateurs par rôle."""
    
    permission_classes = [IsManager]
    
    @swagger_auto_schema(operation_description="Liste les utilisateurs d'un rôle")
    def get(self, request, role_code):
        users = RBACService.get_users_with_role(role_code)
        
        from api.v1.serializers.auth_serializers import UserProfileSerializer
        serializer = UserProfileSerializer(users, many=True)
        
        return success_response(data={
            'role': role_code,
            'count': len(users),
            'users': serializer.data
        })
