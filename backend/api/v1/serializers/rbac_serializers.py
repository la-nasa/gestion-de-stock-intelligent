"""Serializers pour la gestion RBAC."""
from rest_framework import serializers
from apps.roles.models import Role, Permission


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "code", "name", "description", "module", "scope", "is_active"]


class RoleSerializer(serializers.ModelSerializer):
    permissions_count = serializers.SerializerMethodField()
    users_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ["id", "name", "code", "description", "is_system", "is_active", "level", "permissions_count", "users_count", "created_at"]

    def get_permissions_count(self, obj):
        return obj.permissions.count()

    def get_users_count(self, obj):
        from apps.accounts.models import User
        return User.objects.filter(role=obj.code, is_active=True).count()
