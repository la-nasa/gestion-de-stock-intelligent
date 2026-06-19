"""
Tests pour le système RBAC.
"""
import pytest
from rest_framework import status
from apps.roles.models import Role, Permission, RolePermission
from apps.accounts.models import User
from tests.factories.models import UserFactory
from services.rbac_service import RBACService


class TestRBACService:
    """Tests du service RBAC."""
    
    def test_create_role(self, db):
        """Test création rôle."""
        role = RBACService.create_role(
            name='Test Role',
            code='TEST_ROLE',
            description='Rôle de test',
            level=10,
        )
        
        assert role.code == 'TEST_ROLE'
        assert role.level == 10
    
    def test_assign_permission_to_role(self, db):
        """Test assignation permission."""
        role = Role.objects.create(name='Test', code='TEST', level=1)
        perm = Permission.objects.create(
            code='test.perm',
            name='Test Permission',
            module='test',
        )
        
        rp = RBACService.assign_permission_to_role(role, perm)
        assert rp is not None
        
        # Vérifier que la permission est bien assignée
        perms = RBACService.get_role_permissions('TEST')
        assert 'test.perm' in perms
    
    def test_revoke_permission(self, db):
        """Test révocation permission."""
        role = Role.objects.create(name='Test2', code='TEST2', level=1)
        perm = Permission.objects.create(
            code='test.perm2',
            name='Test Permission 2',
            module='test',
        )
        
        RBACService.assign_permission_to_role(role, perm)
        assert 'test.perm2' in RBACService.get_role_permissions('TEST2')
        
        RBACService.revoke_permission_from_role(role, perm)
        assert 'test.perm2' not in RBACService.get_role_permissions('TEST2')
    
    def test_user_has_permission(self, db):
        """Test vérification permission utilisateur."""
        user = UserFactory(role='OPERATOR')
        role = Role.objects.create(
            name='Operator',
            code='OPERATOR',
            level=40,
        )
        perm = Permission.objects.create(
            code='products.view',
            name='Voir produits',
            module='products',
        )
        
        RBACService.assign_permission_to_role(role, perm)
        
        assert RBACService.user_has_permission(user, 'products.view') is True
        assert RBACService.user_has_permission(user, 'nonexistent.perm') is False
    
    def test_admin_has_all_permissions(self, db):
        """Test admin a toutes les permissions."""
        user = UserFactory(role='ADMIN')
        
        Permission.objects.create(
            code='any.perm',
            name='Any Permission',
            module='any',
        )
        
        assert RBACService.user_has_permission(user, 'any.perm') is True
        assert RBACService.user_has_permission(user, 'nonexistent') is True
    
    def test_get_user_permissions(self, db):
        """Test récupération permissions utilisateur."""
        user = UserFactory(role='MANAGER')
        role = Role.objects.create(
            name='Manager',
            code='MANAGER',
            level=80,
        )
        
        perms = [
            Permission.objects.create(code=f'test.{i}', name=f'Perm {i}', module='test')
            for i in range(3)
        ]
        
        RBACService.assign_permissions_to_role_bulk(role, perms)
        
        user_perms = RBACService.get_user_permissions(user)
        assert len(user_perms) == 3
    
    def test_assign_role_to_user(self, db):
        """Test assignation rôle à utilisateur."""
        user = UserFactory(role='VIEWER')
        Role.objects.create(name='Operator', code='OPERATOR', level=40)
        
        RBACService.assign_role_to_user(user, 'OPERATOR')
        assert user.role == 'OPERATOR'


class TestRBACAPI:
    """Tests API RBAC."""
    
    def test_list_roles(self, db, authenticated_client):
        """Test liste rôles."""
        client, user = authenticated_client
        Role.objects.create(name='Test', code='TEST', level=1)
        
        response = client.get('/api/v1/rbac/roles/')
        assert response.status_code == 200
    
    def test_create_role_admin_only(self, db, manager_client):
        """Test création rôle réservée admin."""
        client, user = manager_client
        
        response = client.post('/api/v1/rbac/roles/', {
            'name': 'Nouveau Rôle',
            'code': 'NEW_ROLE',
            'description': 'Test',
            'level': 50,
        }, format='json')
        
        assert response.status_code == 403
    
    def test_view_permissions(self, db, authenticated_client):
        """Test consultation permissions."""
        client, user = authenticated_client
        
        response = client.get('/api/v1/rbac/permissions/')
        assert response.status_code == 200
    
    def test_my_permissions(self, db, authenticated_client):
        """Test consultation de mes permissions."""
        client, user = authenticated_client
        
        response = client.get('/api/v1/rbac/my-permissions/')
        assert response.status_code == 200