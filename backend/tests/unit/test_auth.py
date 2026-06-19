"""
Tests unitaires pour l'authentification.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


class TestUserModel:
    """Tests du modèle User."""
    
    def test_create_user(self, db):
        """Test la création d'un utilisateur."""
        user = User.objects.create_user(
            email='test@test.cm',
            password='TestPass123!',
            first_name='Test',
            last_name='User',
            matricule='TST001'
        )
        
        assert user.email == 'test@test.cm'
        assert user.check_password('TestPass123!')
        assert user.get_full_name() == 'Test User'
        assert user.is_active is True
        assert user.role == 'VIEWER'
    
    def test_create_superuser(self, db):
        """Test la création d'un superuser."""
        user = User.objects.create_superuser(
            email='admin@test.cm',
            password='AdminPass123!',
            first_name='Admin',
            last_name='IUC',
            matricule='ADM001'
        )
        
        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.role == 'ADMIN'
    
    def test_user_str(self, db):
        """Test la représentation string."""
        user = User.objects.create_user(
            email='test@test.cm',
            first_name='Jean',
            last_name='Kouam',
            matricule='TST002'
        )
        assert 'Jean Kouam' in str(user)
    
    def test_unique_email(self, db):
        """Test l'unicité de l'email."""
        User.objects.create_user(
            email='test@test.cm',
            first_name='User1',
            last_name='Test',
            matricule='TST003'
        )
        
        with pytest.raises(Exception):
            User.objects.create_user(
                email='test@test.cm',
                first_name='User2',
                last_name='Test',
                matricule='TST004'
            )


class TestAuthAPI:
    """Tests des endpoints d'authentification."""
    
    def test_login_success(self, db, api_client):
        """Test connexion réussie."""
        user = User.objects.create_user(
            email='login@test.cm',
            password='TestPass123!',
            first_name='Login',
            last_name='Test',
            matricule='LOG001'
        )
        
        response = api_client.post('/api/v1/auth/login/', {
            'email': 'login@test.cm',
            'password': 'TestPass123!',
        }, format='json')
        
        assert response.status_code == 200
        data = response.data
        assert data['success'] is True
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']
    
    def test_login_failure(self, db, api_client):
        """Test connexion échouée."""
        response = api_client.post('/api/v1/auth/login/', {
            'email': 'nonexistent@test.cm',
            'password': 'WrongPass!',
        }, format='json')
        
        assert response.status_code == 401
        assert response.data['success'] is False
    
    def test_register_success(self, db, api_client):
        """Test inscription réussie."""
        response = api_client.post('/api/v1/auth/register/', {
            'email': 'newuser@test.cm',
            'password': 'NewPass123!',
            'password_confirm': 'NewPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'matricule': 'NEW001',
        }, format='json')
        
        assert response.status_code == 201
        assert response.data['success'] is True
        assert User.objects.filter(email='newuser@test.cm').exists()
    
    def test_register_password_mismatch(self, db, api_client):
        """Test inscription avec mots de passe différents."""
        response = api_client.post('/api/v1/auth/register/', {
            'email': 'mismatch@test.cm',
            'password': 'Pass123!',
            'password_confirm': 'Pass456!',
            'first_name': 'Mismatch',
            'last_name': 'User',
            'matricule': 'MIS001',
        }, format='json')
        
        assert response.status_code == 400
    
    def test_register_weak_password(self, db, api_client):
        """Test inscription avec mot de passe faible."""
        response = api_client.post('/api/v1/auth/register/', {
            'email': 'weak@test.cm',
            'password': '123',
            'password_confirm': '123',
            'first_name': 'Weak',
            'last_name': 'Pass',
            'matricule': 'WEA001',
        }, format='json')
        
        assert response.status_code == 400
    
    def test_profile_authenticated(self, db, authenticated_client):
        """Test accès au profil authentifié."""
        client, user = authenticated_client
        response = client.get('/api/v1/auth/profile/')
        
        assert response.status_code == 200
        assert response.data['data']['email'] == user.email
    
    def test_profile_unauthenticated(self, db, api_client):
        """Test accès au profil sans authentification."""
        response = api_client.get('/api/v1/auth/profile/')
        assert response.status_code == 401
    
    def test_refresh_token(self, db, api_client):
        """Test rafraîchissement de token."""
        user = User.objects.create_user(
            email='refresh@test.cm',
            password='TestPass123!',
            first_name='Refresh',
            last_name='Test',
            matricule='REF001'
        )
        
        # Login
        login_resp = api_client.post('/api/v1/auth/login/', {
            'email': 'refresh@test.cm',
            'password': 'TestPass123!',
        }, format='json')
        
        refresh_token = login_resp.data['data']['refresh_token']
        
        # Refresh
        response = api_client.post('/api/v1/auth/refresh/', {
            'refresh_token': refresh_token,
        }, format='json')
        
        assert response.status_code == 200
        assert 'access_token' in response.data['data']
    
    def test_logout(self, db, api_client):
        """Test déconnexion."""
        user = User.objects.create_user(
            email='logout@test.cm',
            password='TestPass123!',
            first_name='Logout',
            last_name='Test',
            matricule='OUT001'
        )
        
        login_resp = api_client.post('/api/v1/auth/login/', {
            'email': 'logout@test.cm',
            'password': 'TestPass123!',
        }, format='json')
        
        token = login_resp.data['data']['access_token']
        refresh = login_resp.data['data']['refresh_token']
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.post('/api/v1/auth/logout/', {
            'refresh_token': refresh,
        }, format='json')
        
        assert response.status_code == 200