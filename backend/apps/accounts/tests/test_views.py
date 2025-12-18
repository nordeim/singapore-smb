"""
API tests for accounts views.

Tests:
- Authentication endpoints (login, logout, refresh)
- Company CRUD
- User CRUD
- Role CRUD
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.accounts.models import Company, User, Role, UserRole
from apps.accounts.tests.factories import (
    CompanyFactory, UserFactory, SuperUserFactory,
    RoleFactory, UserRoleFactory
)


pytestmark = pytest.mark.django_db


# =============================================================================
# AUTH ENDPOINT TESTS
# =============================================================================

class TestAuthEndpoints:
    """Tests for authentication endpoints."""
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    @pytest.fixture
    def user_with_password(self):
        user = UserFactory()
        user.set_password('testpass123')
        user.save()
        return user
    
    def test_login_success(self, api_client, user_with_password):
        """Test successful login."""
        response = api_client.post(
            '/api/v1/accounts/auth/login/',
            {
                'email': user_with_password.email,
                'password': 'testpass123'
            },
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
    
    def test_login_invalid_credentials(self, api_client, user_with_password):
        """Test login with invalid password."""
        response = api_client.post(
            '/api/v1/accounts/auth/login/',
            {
                'email': user_with_password.email,
                'password': 'wrongpassword'
            },
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_nonexistent_user(self, api_client):
        """Test login with nonexistent email."""
        response = api_client.post(
            '/api/v1/accounts/auth/login/',
            {
                'email': 'nouser@example.com',
                'password': 'password'
            },
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_logout(self, api_client, user_with_password):
        """Test logout endpoint."""
        # Login first
        login_response = api_client.post(
            '/api/v1/accounts/auth/login/',
            {
                'email': user_with_password.email,
                'password': 'testpass123'
            },
            format='json'
        )
        
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {login_response.data["access"]}'
        )
        
        response = api_client.post(
            '/api/v1/accounts/auth/logout/',
            {'refresh': login_response.data['refresh']},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_token_refresh(self, api_client, user_with_password):
        """Test token refresh endpoint."""
        # Login first
        login_response = api_client.post(
            '/api/v1/accounts/auth/login/',
            {
                'email': user_with_password.email,
                'password': 'testpass123'
            },
            format='json'
        )
        
        response = api_client.post(
            '/api/v1/accounts/auth/refresh/',
            {'refresh': login_response.data['refresh']},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
    
    def test_current_user(self, api_client, user_with_password):
        """Test current user endpoint."""
        # Login first
        login_response = api_client.post(
            '/api/v1/accounts/auth/login/',
            {
                'email': user_with_password.email,
                'password': 'testpass123'
            },
            format='json'
        )
        
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {login_response.data["access"]}'
        )
        
        response = api_client.get('/api/v1/accounts/auth/me/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user_with_password.email


# =============================================================================
# USER ENDPOINT TESTS
# =============================================================================

class TestUserEndpoints:
    """Tests for user management endpoints."""
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    @pytest.fixture
    def authenticated_user(self, api_client):
        user = UserFactory()
        user.set_password('testpass123')
        user.save()
        
        # Login
        response = api_client.post(
            '/api/v1/accounts/auth/login/',
            {'email': user.email, 'password': 'testpass123'},
            format='json'
        )
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}'
        )
        return user
    
    def test_list_users_in_company(self, api_client, authenticated_user):
        """Test listing users in same company."""
        # Create another user in same company
        UserFactory(company=authenticated_user.company)
        
        response = api_client.get('/api/v1/accounts/users/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_get_user_profile(self, api_client, authenticated_user):
        """Test getting user profile."""
        response = api_client.get('/api/v1/accounts/users/me/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == authenticated_user.email
    
    def test_update_user_profile(self, api_client, authenticated_user):
        """Test updating user profile."""
        response = api_client.patch(
            '/api/v1/accounts/users/update_profile/',
            {'first_name': 'Updated'},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
    
    def test_change_password(self, api_client, authenticated_user):
        """Test password change."""
        response = api_client.post(
            '/api/v1/accounts/users/change_password/',
            {
                'current_password': 'testpass123',
                'new_password': 'newpass456!',
                'new_password_confirm': 'newpass456!'
            },
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK


# =============================================================================
# COMPANY ENDPOINT TESTS
# =============================================================================

class TestCompanyEndpoints:
    """Tests for company management endpoints."""
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    def test_create_company_unauthenticated(self, api_client):
        """Test company creation without authentication (registration)."""
        response = api_client.post(
            '/api/v1/accounts/companies/',
            {
                'name': 'New Corp',
                'uen': '201812345A',
                'email': 'company@example.com',
                'owner_email': 'owner@example.com',
                'owner_password': 'SecurePass123!'
            },
            format='json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Corp'
    
    def test_get_own_company(self, api_client):
        """Test getting own company details."""
        user = UserFactory()
        user.set_password('testpass123')
        user.save()
        
        response = api_client.post(
            '/api/v1/accounts/auth/login/',
            {'email': user.email, 'password': 'testpass123'},
            format='json'
        )
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}'
        )
        
        response = api_client.get(
            f'/api/v1/accounts/companies/{user.company.id}/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(user.company.id)


# =============================================================================
# ROLE ENDPOINT TESTS
# =============================================================================

class TestRoleEndpoints:
    """Tests for role management endpoints."""
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    @pytest.fixture
    def authenticated_user(self, api_client):
        user = UserFactory()
        user.set_password('testpass123')
        user.save()
        
        response = api_client.post(
            '/api/v1/accounts/auth/login/',
            {'email': user.email, 'password': 'testpass123'},
            format='json'
        )
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}'
        )
        return user
    
    def test_list_company_roles(self, api_client, authenticated_user):
        """Test listing roles in company."""
        RoleFactory(company=authenticated_user.company)
        
        response = api_client.get('/api/v1/accounts/roles/')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_create_role(self, api_client, authenticated_user):
        """Test creating a new role."""
        response = api_client.post(
            '/api/v1/accounts/roles/',
            {
                'name': 'custom_role',
                'description': 'A custom role',
                'permissions': ['orders.view']
            },
            format='json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'custom_role'
