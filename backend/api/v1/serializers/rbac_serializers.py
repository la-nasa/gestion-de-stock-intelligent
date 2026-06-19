"""
Serializers pour la gestion RBAC.
"""
from rest_framework import serializers
from apps.roles.models import Role, Permission, RolePermission
from apps.accounts.models import User


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer pour les permissions."""
    
    class Meta:
        model = Permission
        fields = [
            'id', 'code', 'name', 'description',
            'module', 'scope', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PermissionListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour liste de permissions."""
    
    class Meta:
        model = Permission
        fields = ['id', 'code', 'name', 'module', 'scope']


class RolePermissionSerializer(serializers.ModelSerializer):
    """Serializer pour l'association rôle-permission."""
    
    permission = PermissionListSerializer(read_only=True)
    permission_code = serializers.CharField(write_only=True)
    granted_by_name = serializers.CharField(
        source='granted_by.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = RolePermission
        fields = [
            'id', 'permission', 'permission_code',
            'granted_by', 'granted_by_name',
            'created_at'
        ]
        read_only_fields = ['id', 'granted_by', 'created_at']
    
    def validate_permission_code(self, value):
        """Valide que la permission existe."""
        if not Permission.objects.filter(code=value, is_active=True).exists():
            raise serializers.ValidationError(f"Permission '{value}' introuvable.")
        return value


class RoleSerializer(serializers.ModelSerializer):
    """Serializer pour les rôles."""
    
    permissions = PermissionListSerializer(many=True, read_only=True)
    permissions_count = serializers.SerializerMethodField()
    users_count = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'code', 'description',
            'is_system', 'is_active', 'level',
            'parent', 'parent_name',
            'permissions', 'permissions_count',
            'users_count', 'children_names',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_system', 'created_at', 'updated_at']
    
    def get_permissions_count(self, obj):
        return obj.permissions.count()
    
    def get_users_count(self, obj):
        return User.objects.filter(role=obj.code, is_active=True).count()
    
    def get_children_names(self, obj):
        return list(obj.children.values_list('name', flat=True))
    
    def validate_code(self, value):
        """Valide le format et l'unicité du code."""
        value = value.upper().strip()
        if not value.isalnum():
            raise serializers.ValidationError("Le code doit être alphanumérique.")
        
        # Vérifier l'unicité (exclure l'instance actuelle en cas d'update)
        qs = Role.objects.filter(code=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("Ce code est déjà utilisé.")
        
        return value


class RoleCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de rôle."""
    
    permission_codes = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text="Liste des codes de permissions à assigner"
    )
    
    class Meta:
        model = Role
        fields = [
            'name', 'code', 'description',
            'parent', 'level', 'permission_codes'
        ]
    
    def create(self, validated_data):
        permission_codes = validated_data.pop('permission_codes', [])
        role = Role.objects.create(**validated_data)
        
        # Assigner les permissions
        if permission_codes:
            permissions = Permission.objects.filter(
                code__in=permission_codes,
                is_active=True
            )
            from services.rbac_service import RBACService
            RBACService.assign_permissions_to_role_bulk(
                role, list(permissions),
                granted_by=self.context['request'].user
            )
        
        return role


class AssignRoleSerializer(serializers.Serializer):
    """Serializer pour assigner un rôle à un utilisateur."""
    
    user_id = serializers.UUIDField(required=True)
    role_code = serializers.CharField(required=True)
    
    def validate_user_id(self, value):
        try:
            user = User.objects.get(id=value, is_active=True)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("Utilisateur introuvable.")
    
    def validate_role_code(self, value):
        try:
            role = Role.objects.get(code=value, is_active=True)
            return role
        except Role.DoesNotExist:
            raise serializers.ValidationError("Rôle introuvable.")


class BulkPermissionAssignSerializer(serializers.Serializer):
    """Serializer pour l'assignation en masse de permissions."""
    
    permission_codes = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        min_length=1
    )
    
    def validate_permission_codes(self, value):
        """Vérifie que toutes les permissions existent."""
        existing = set(
            Permission.objects.filter(
                code__in=value,
                is_active=True
            ).values_list('code', flat=True)
        )
        invalid = set(value) - existing
        if invalid:
            raise serializers.ValidationError(
                f"Permissions invalides : {', '.join(invalid)}"
            )
        return value


class UserPermissionsSerializer(serializers.Serializer):
    """Serializer pour afficher les permissions d'un utilisateur."""
    
    user = serializers.SerializerMethodField()
    role = serializers.CharField()
    permissions = serializers.ListField(child=serializers.CharField())
    total = serializers.IntegerField()
    
    def get_user(self, obj):
        return {
            'id': str(obj['user'].id),
            'email': obj['user'].email,
            'full_name': obj['user'].get_full_name()
        }
