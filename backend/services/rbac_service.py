"""
Service de gestion RBAC (Role-Based Access Control).
"""
from typing import List, Optional, Set
from django.db import transaction
from django.core.cache import cache
from django.conf import settings
from apps.accounts.models import User
from apps.roles.models import Role, Permission, RolePermission


class RBACService:
    """Service de gestion des rôles et permissions."""
    
    CACHE_KEY_PREFIX = 'rbac:'
    CACHE_TIMEOUT = 3600  # 1 heure
    
    # ==========================================
    # GESTION DES RÔLES
    # ==========================================
    
    @staticmethod
    def create_role(name: str, code: str, description: str = '',
                    parent: Optional[Role] = None, level: int = 0,
                    is_system: bool = False) -> Role:
        """Crée un nouveau rôle."""
        role = Role.objects.create(
            name=name,
            code=code,
            description=description,
            parent=parent,
            level=level,
            is_system=is_system
        )
        return role
    
    @staticmethod
    def update_role(role: Role, **kwargs) -> Role:
        """Met à jour un rôle."""
        for key, value in kwargs.items():
            if hasattr(role, key):
                setattr(role, key, value)
        role.save()
        # Invalider le cache
        RBACService._invalidate_role_cache(role)
        return role
    
    @staticmethod
    def delete_role(role: Role) -> bool:
        """Supprime un rôle (soft delete)."""
        if role.is_system:
            raise ValueError("Impossible de supprimer un rôle système.")
        role.soft_delete()
        RBACService._invalidate_role_cache(role)
        return True
    
    @staticmethod
    def get_role_by_code(code: str) -> Optional[Role]:
        """Récupère un rôle par son code."""
        return Role.objects.filter(code=code, is_deleted=False).first()
    
    @staticmethod
    def get_all_roles() -> List[Role]:
        """Récupère tous les rôles actifs."""
        return list(Role.objects.filter(is_active=True, is_deleted=False))
    
    @staticmethod
    def get_role_hierarchy(role: Role) -> List[Role]:
        """Récupère la hiérarchie d'un rôle (parents)."""
        hierarchy = []
        current = role.parent
        while current:
            hierarchy.append(current)
            current = current.parent
        return hierarchy
    
    # ==========================================
    # GESTION DES PERMISSIONS
    # ==========================================
    
    @staticmethod
    def create_permission(code: str, name: str, module: str,
                          description: str = '',
                          scope: str = 'GLOBAL') -> Permission:
        """Crée une nouvelle permission."""
        permission = Permission.objects.create(
            code=code,
            name=name,
            module=module,
            description=description,
            scope=scope
        )
        return permission
    
    @staticmethod
    def get_permission_by_code(code: str) -> Optional[Permission]:
        """Récupère une permission par son code."""
        return Permission.objects.filter(code=code, is_active=True).first()
    
    @staticmethod
    def get_all_permissions() -> List[Permission]:
        """Récupère toutes les permissions actives."""
        return list(Permission.objects.filter(is_active=True))
    
    @staticmethod
    def get_permissions_by_module(module: str) -> List[Permission]:
        """Récupère les permissions d'un module."""
        return list(Permission.objects.filter(module=module, is_active=True))
    
    # ==========================================
    # GESTION DES ASSIGNATIONS
    # ==========================================
    
    @staticmethod
    @transaction.atomic
    def assign_permission_to_role(role: Role, permission: Permission,
                                   granted_by: Optional[User] = None) -> RolePermission:
        """Assigne une permission à un rôle."""
        rp, created = RolePermission.objects.get_or_create(
            role=role,
            permission=permission,
            defaults={'granted_by': granted_by}
        )
        if not created:
            raise ValueError(f"La permission {permission.code} est déjà assignée au rôle {role.code}")
        
        # Invalider le cache
        RBACService._invalidate_permission_cache(role)
        return rp
    
    @staticmethod
    @transaction.atomic
    def revoke_permission_from_role(role: Role, permission: Permission) -> bool:
        """Révoque une permission d'un rôle."""
        deleted, _ = RolePermission.objects.filter(
            role=role,
            permission=permission
        ).delete()
        
        if deleted:
            RBACService._invalidate_permission_cache(role)
        return deleted > 0
    
    @staticmethod
    @transaction.atomic
    def assign_permissions_to_role_bulk(role: Role,
                                         permissions: List[Permission],
                                         granted_by: Optional[User] = None) -> int:
        """Assigne plusieurs permissions à un rôle."""
        count = 0
        existing = set(
            RolePermission.objects.filter(role=role)
            .values_list('permission_id', flat=True)
        )
        
        to_create = []
        for permission in permissions:
            if permission.id not in existing:
                to_create.append(RolePermission(
                    role=role,
                    permission=permission,
                    granted_by=granted_by
                ))
        
        if to_create:
            RolePermission.objects.bulk_create(to_create, ignore_conflicts=True)
            count = len(to_create)
            RBACService._invalidate_permission_cache(role)
        
        return count
    
    @staticmethod
    def assign_role_to_user(user: User, role_code: str) -> User:
        """Assigne un rôle à un utilisateur (via le champ role)."""
        role = RBACService.get_role_by_code(role_code)
        if not role:
            raise ValueError(f"Rôle {role_code} introuvable.")
        
        user.role = role_code
        user.save(update_fields=['role'])
        RBACService._invalidate_user_cache(user)
        return user
    
    # ==========================================
    # VÉRIFICATION DES PERMISSIONS
    # ==========================================
    
    @staticmethod
    def user_has_permission(user: User, permission_code: str) -> bool:
        """Vérifie si un utilisateur a une permission spécifique."""
        if not user.is_authenticated:
            return False
        
        # Les admins ont toutes les permissions
        if user.role == 'ADMIN':
            return True
        
        # Vérifier le cache
        cache_key = f"{RBACService.CACHE_KEY_PREFIX}user:{user.id}:perm:{permission_code}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        
        # Vérifier les permissions du rôle
        has_perm = RolePermission.objects.filter(
            role__code=user.role,
            permission__code=permission_code,
            role__is_active=True,
            permission__is_active=True
        ).exists()
        
        # Mettre en cache
        cache.set(cache_key, has_perm, RBACService.CACHE_TIMEOUT)
        
        return has_perm
    
    @staticmethod
    def user_has_any_permission(user: User, permission_codes: List[str]) -> bool:
        """Vérifie si un utilisateur a au moins une des permissions."""
        return any(
            RBACService.user_has_permission(user, code)
            for code in permission_codes
        )
    
    @staticmethod
    def user_has_all_permissions(user: User, permission_codes: List[str]) -> bool:
        """Vérifie si un utilisateur a toutes les permissions."""
        return all(
            RBACService.user_has_permission(user, code)
            for code in permission_codes
        )
    
    @staticmethod
    def get_user_permissions(user: User) -> Set[str]:
        """Récupère toutes les permissions d'un utilisateur."""
        if user.role == 'ADMIN':
            return set(Permission.objects.filter(is_active=True)
                      .values_list('code', flat=True))
        
        cache_key = f"{RBACService.CACHE_KEY_PREFIX}user:{user.id}:permissions"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        permissions = set(
            RolePermission.objects.filter(
                role__code=user.role,
                role__is_active=True,
                permission__is_active=True
            ).values_list('permission__code', flat=True)
        )
        
        cache.set(cache_key, permissions, RBACService.CACHE_TIMEOUT)
        return permissions
    
    @staticmethod
    def get_role_permissions(role_code: str) -> Set[str]:
        """Récupère toutes les permissions d'un rôle."""
        cache_key = f"{RBACService.CACHE_KEY_PREFIX}role:{role_code}:permissions"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        permissions = set(
            RolePermission.objects.filter(
                role__code=role_code,
                role__is_active=True,
                permission__is_active=True
            ).values_list('permission__code', flat=True)
        )
        
        cache.set(cache_key, permissions, RBACService.CACHE_TIMEOUT)
        return permissions
    
    @staticmethod
    def get_users_with_role(role_code: str) -> List[User]:
        """Récupère tous les utilisateurs avec un rôle spécifique."""
        return list(User.objects.filter(role=role_code, is_active=True))
    
    # ==========================================
    # GESTION DU CACHE
    # ==========================================
    
    @staticmethod
    def _invalidate_user_cache(user: User):
        """Invalide le cache pour un utilisateur."""
        pattern = f"{RBACService.CACHE_KEY_PREFIX}user:{user.id}:*"
        # Redis cache invalidation
        try:
            from django_redis import get_redis_connection
            redis = get_redis_connection('default')
            keys = redis.keys(pattern)
            if keys:
                redis.delete(*keys)
        except Exception:
            pass
    
    @staticmethod
    def _invalidate_role_cache(role: Role):
        """Invalide le cache pour un rôle."""
        pattern = f"{RBACService.CACHE_KEY_PREFIX}role:{role.code}:*"
        try:
            from django_redis import get_redis_connection
            redis = get_redis_connection('default')
            keys = redis.keys(pattern)
            if keys:
                redis.delete(*keys)
        except Exception:
            pass
        # Invalider aussi les caches des utilisateurs avec ce rôle
        users = User.objects.filter(role=role.code)
        for user in users:
            RBACService._invalidate_user_cache(user)
    
    @staticmethod
    def _invalidate_permission_cache(role: Role):
        """Invalide le cache des permissions pour un rôle."""
        cache_key = f"{RBACService.CACHE_KEY_PREFIX}role:{role.code}:permissions"
        cache.delete(cache_key)
        # Invalider aussi les caches des utilisateurs
        users = User.objects.filter(role=role.code)
        for user in users:
            cache_key_user = f"{RBACService.CACHE_KEY_PREFIX}user:{user.id}:permissions"
            cache.delete(cache_key_user)
    
    @staticmethod
    def clear_all_cache():
        """Vide tout le cache RBAC."""
        try:
            from django_redis import get_redis_connection
            redis = get_redis_connection('default')
            keys = redis.keys(f"{RBACService.CACHE_KEY_PREFIX}*")
            if keys:
                redis.delete(*keys)
        except Exception:
            pass
