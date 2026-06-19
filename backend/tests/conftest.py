"""
Fixtures partagées pour tous les tests.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from model_bakery import baker

User = get_user_model()


@pytest.fixture
def api_client():
    """Client API non authentifié."""
    return APIClient()


@pytest.fixture
def authenticated_client():
    """Client API authentifié en tant qu'admin."""
    user = baker.make(User, email='admin@test.cm', role='ADMIN', is_active=True)
    user.set_password('TestPass123!')
    user.save()
    
    client = APIClient()
    response = client.post('/api/v1/auth/login/', {
        'email': 'admin@test.cm',
        'password': 'TestPass123!',
    }, format='json')
    
    if response.status_code == 200:
        token = response.data['data']['access_token']
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    return client, user


@pytest.fixture
def manager_client():
    """Client API authentifié en tant que manager."""
    user = baker.make(User, email='manager@test.cm', role='MANAGER', is_active=True)
    user.set_password('TestPass123!')
    user.save()
    
    client = APIClient()
    response = client.post('/api/v1/auth/login/', {
        'email': 'manager@test.cm',
        'password': 'TestPass123!',
    }, format='json')
    
    if response.status_code == 200:
        token = response.data['data']['access_token']
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    return client, user


@pytest.fixture
def operator_client():
    """Client API authentifié en tant qu'opérateur."""
    user = baker.make(User, email='operator@test.cm', role='OPERATOR', is_active=True)
    user.set_password('TestPass123!')
    user.save()
    
    client = APIClient()
    response = client.post('/api/v1/auth/login/', {
        'email': 'operator@test.cm',
        'password': 'TestPass123!',
    }, format='json')
    
    if response.status_code == 200:
        token = response.data['data']['access_token']
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    return client, user


@pytest.fixture
def viewer_client():
    """Client API authentifié en tant que viewer."""
    user = baker.make(User, email='viewer@test.cm', role='VIEWER', is_active=True)
    user.set_password('TestPass123!')
    user.save()
    
    client = APIClient()
    response = client.post('/api/v1/auth/login/', {
        'email': 'viewer@test.cm',
        'password': 'TestPass123!',
    }, format='json')
    
    if response.status_code == 200:
        token = response.data['data']['access_token']
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    return client, user