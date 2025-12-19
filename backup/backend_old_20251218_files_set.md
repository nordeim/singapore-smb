# backend/.env.example
```example
# Django settings
DJANGO_SETTINGS_MODULE=config.settings.development
SECRET_KEY=django-insecure-dev-key-change-in-production

# Database
DB_NAME=singapore_smb
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DATABASE_URL=postgres://postgres:postgres@localhost:5432/singapore_smb

# Redis
REDIS_URL=redis://localhost:6379/0

# Debug
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Logging
DJANGO_LOG_LEVEL=INFO

```

# backend/.python-version
```txt
3.12

```

# backend/apps/accounts/apps.py
```py
"""
Django app configuration for accounts module.
"""
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Configuration for the accounts app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'User Accounts'
    
    def ready(self):
        """
        Called when Django starts.
        Import signals to register them.
        """
        try:
            import apps.accounts.signals  # noqa: F401
        except ImportError:
            pass

```

# backend/apps/accounts/__init__.py
```py
"""Accounts app for user and company management."""

```

# backend/apps/accounts/tests/__init__.py
```py
"""Tests package for accounts app."""

```

# backend/apps/accounts/tests/test_views.py
```py
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

```

# backend/apps/accounts/tests/factories.py
```py
"""
Factory classes for accounts tests.

Uses factory_boy to create test data for:
- Company
- User
- Role
- UserRole
"""
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.hashers import make_password

from apps.accounts.models import Company, User, Role, UserRole


class CompanyFactory(DjangoModelFactory):
    """Factory for creating Company instances."""
    
    class Meta:
        model = Company
    
    name = factory.Faker('company')
    legal_name = factory.LazyAttribute(lambda obj: f"{obj.name} Pte Ltd")
    uen = factory.Sequence(lambda n: f'2024{n:05d}A')
    email = factory.Faker('company_email')
    phone = factory.Faker('phone_number')
    address_line1 = factory.Faker('street_address')
    postal_code = factory.Sequence(lambda n: f'{100000 + n:06d}'[:6])
    plan_tier = 'standard'
    gst_registered = False


class GSTRegisteredCompanyFactory(CompanyFactory):
    """Factory for creating GST-registered companies."""
    
    gst_registered = True
    gst_registration_number = factory.Sequence(lambda n: f'M{n:08d}')
    gst_registration_date = factory.Faker('date_this_decade')


class UserFactory(DjangoModelFactory):
    """Factory for creating User instances."""
    
    class Meta:
        model = User
    
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    phone = factory.Faker('phone_number')
    company = factory.SubFactory(CompanyFactory)
    is_active = True
    is_verified = True
    password = factory.LazyFunction(lambda: make_password('testpass123'))
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override to handle password properly."""
        password = kwargs.pop('password', None)
        user = super()._create(model_class, *args, **kwargs)
        if password and not password.startswith('pbkdf2_'):
            user.set_password(password)
            user.save()
        return user


class SuperUserFactory(UserFactory):
    """Factory for creating superusers."""
    
    is_staff = True
    is_superuser = True
    company = None


class RoleFactory(DjangoModelFactory):
    """Factory for creating Role instances."""
    
    class Meta:
        model = Role
    
    name = factory.Sequence(lambda n: f'role_{n}')
    description = factory.Faker('sentence')
    company = factory.SubFactory(CompanyFactory)
    permissions = factory.LazyFunction(lambda: ['users.view', 'orders.view'])
    is_system = False


class OwnerRoleFactory(RoleFactory):
    """Factory for creating owner roles."""
    
    name = 'owner'
    description = 'Company owner with full access'
    permissions = factory.LazyFunction(lambda: ['all'])


class AdminRoleFactory(RoleFactory):
    """Factory for creating admin roles."""
    
    name = 'admin'
    description = 'Administrative access'
    permissions = factory.LazyFunction(lambda: [
        'users.view', 'users.create', 'users.update', 'users.delete',
        'products.view', 'products.create', 'products.update', 'products.delete',
        'orders.view', 'orders.update',
    ])


class UserRoleFactory(DjangoModelFactory):
    """Factory for creating UserRole instances."""
    
    class Meta:
        model = UserRole
    
    user = factory.SubFactory(UserFactory)
    role = factory.SubFactory(RoleFactory)
    assigned_by = None

```

# backend/apps/accounts/tests/test_services.py
```py
"""
Unit tests for accounts services.

Tests:
- AuthService (authentication, tokens)
- UserService (user management)
- CompanyService (company management)
"""
import pytest
from django.utils import timezone
from unittest.mock import patch, MagicMock

from apps.accounts.models import Company, User, Role, UserRole
from apps.accounts.services import AuthService, UserService, CompanyService
from apps.accounts.tests.factories import (
    CompanyFactory, UserFactory, RoleFactory
)


pytestmark = pytest.mark.django_db


# =============================================================================
# AUTH SERVICE TESTS
# =============================================================================

class TestAuthService:
    """Tests for AuthService."""
    
    def test_authenticate_valid_credentials(self):
        """Test authentication with valid credentials."""
        user = UserFactory()
        user.set_password('testpass123')
        user.save()
        
        authenticated = AuthService.authenticate(user.email, 'testpass123')
        
        assert authenticated is not None
        assert authenticated.id == user.id
    
    def test_authenticate_invalid_password(self):
        """Test authentication with invalid password."""
        user = UserFactory()
        user.set_password('correctpass')
        user.save()
        
        authenticated = AuthService.authenticate(user.email, 'wrongpass')
        
        assert authenticated is None
    
    def test_authenticate_nonexistent_user(self):
        """Test authentication with nonexistent email."""
        authenticated = AuthService.authenticate('nouser@example.com', 'password')
        
        assert authenticated is None
    
    def test_authenticate_locked_account(self):
        """Test authentication with locked account."""
        user = UserFactory()
        user.set_password('testpass123')
        user.locked_until = timezone.now() + timezone.timedelta(hours=1)
        user.save()
        
        authenticated = AuthService.authenticate(user.email, 'testpass123')
        
        assert authenticated is None
    
    def test_authenticate_inactive_user(self):
        """Test authentication with inactive user."""
        user = UserFactory(is_active=False)
        user.set_password('testpass123')
        user.save()
        
        authenticated = AuthService.authenticate(user.email, 'testpass123')
        
        assert authenticated is None
    
    def test_generate_tokens(self):
        """Test JWT token generation."""
        user = UserFactory()
        
        tokens = AuthService.generate_tokens(user)
        
        assert 'access' in tokens
        assert 'refresh' in tokens
        assert tokens['access'] != ''
        assert tokens['refresh'] != ''
    
    def test_refresh_token(self):
        """Test token refresh."""
        user = UserFactory()
        tokens = AuthService.generate_tokens(user)
        
        new_tokens = AuthService.refresh_token(tokens['refresh'])
        
        assert 'access' in new_tokens
        assert new_tokens['access'] != tokens['access']


# =============================================================================
# USER SERVICE TESTS
# =============================================================================

class TestUserService:
    """Tests for UserService."""
    
    def test_create_user(self):
        """Test user creation via service."""
        company = CompanyFactory()
        
        user = UserService.create_user(
            email='newuser@example.com',
            password='securepass123',
            company=company,
            first_name='John',
            last_name='Doe'
        )
        
        assert user.id is not None
        assert user.email == 'newuser@example.com'
        assert user.company == company
        assert user.check_password('securepass123')
    
    def test_create_user_with_roles(self):
        """Test user creation with role assignment."""
        company = CompanyFactory()
        role = RoleFactory(name='admin', company=company)
        
        user = UserService.create_user(
            email='admin@example.com',
            password='securepass123',
            company=company,
            role_names=['admin']
        )
        
        assert 'admin' in list(user.roles.values_list('name', flat=True))
    
    def test_update_user(self):
        """Test user profile update."""
        user = UserFactory(first_name='Old', last_name='Name')
        
        updated = UserService.update_user(
            user,
            first_name='New',
            last_name='Name'
        )
        
        assert updated.first_name == 'New'
    
    def test_change_password(self):
        """Test password change."""
        user = UserFactory()
        user.set_password('oldpass')
        user.save()
        
        UserService.change_password(user, 'newpass123')
        
        assert user.check_password('newpass123')
    
    def test_assign_role(self):
        """Test role assignment."""
        company = CompanyFactory()
        user = UserFactory(company=company)
        role = RoleFactory(company=company)
        
        user_role = UserService.assign_role(user, role)
        
        assert user_role.user == user
        assert user_role.role == role
    
    def test_remove_role(self):
        """Test role removal."""
        company = CompanyFactory()
        user = UserFactory(company=company)
        role = RoleFactory(company=company)
        UserRole.objects.create(user=user, role=role)
        
        removed = UserService.remove_role(user, role)
        
        assert removed is True
        assert role not in user.roles
    
    def test_has_permission(self):
        """Test permission checking."""
        company = CompanyFactory()
        user = UserFactory(company=company)
        role = RoleFactory(company=company, permissions=['orders.view'])
        UserRole.objects.create(user=user, role=role)
        
        assert UserService.has_permission(user, 'orders.view') is True
        assert UserService.has_permission(user, 'orders.delete') is False


# =============================================================================
# COMPANY SERVICE TESTS
# =============================================================================

class TestCompanyService:
    """Tests for CompanyService."""
    
    def test_create_company_with_owner(self):
        """Test company creation with owner user."""
        company, owner = CompanyService.create_company(
            name='Test Corp',
            uen='201812345A',
            email='company@example.com',
            owner_email='owner@example.com',
            owner_password='securepass123'
        )
        
        assert company.id is not None
        assert company.name == 'Test Corp'
        assert owner.email == 'owner@example.com'
        assert owner.company == company
    
    def test_create_company_creates_default_roles(self):
        """Test default roles are created for new company."""
        company, owner = CompanyService.create_company(
            name='Test Corp',
            uen='201812345B',
            email='company@example.com',
            owner_email='owner@example.com',
            owner_password='securepass123'
        )
        
        roles = list(company.roles.values_list('name', flat=True))
        assert 'owner' in roles
        assert 'admin' in roles
        assert 'finance' in roles
    
    def test_owner_has_owner_role(self):
        """Test owner user is assigned owner role."""
        company, owner = CompanyService.create_company(
            name='Test Corp',
            uen='201812345C',
            email='company@example.com',
            owner_email='owner@example.com',
            owner_password='securepass123'
        )
        
        owner_roles = list(owner.roles.values_list('name', flat=True))
        assert 'owner' in owner_roles
    
    def test_check_gst_threshold_below(self):
        """Test GST threshold check - below threshold."""
        company = CompanyFactory()
        
        should_register = CompanyService.check_gst_threshold(company, 500000)
        
        assert should_register is False
    
    def test_check_gst_threshold_above(self):
        """Test GST threshold check - above threshold."""
        company = CompanyFactory()
        
        should_register = CompanyService.check_gst_threshold(company, 1500000)
        
        assert should_register is True
    
    def test_create_default_roles(self):
        """Test default role creation."""
        company = CompanyFactory()
        
        roles = CompanyService.create_default_roles(company)
        
        assert len(roles) == 5  # owner, admin, finance, warehouse, sales

```

# backend/apps/accounts/tests/test_models.py
```py
"""
Unit tests for accounts models.

Tests:
- Company model (UEN validation, GST fields)
- User model (email auth, password, locking)
- Role model (permissions)
- UserRole model (assignments)
"""
import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from apps.accounts.models import Company, User, Role, UserRole
from apps.accounts.tests.factories import (
    CompanyFactory, GSTRegisteredCompanyFactory,
    UserFactory, SuperUserFactory,
    RoleFactory, OwnerRoleFactory,
    UserRoleFactory,
)


pytestmark = pytest.mark.django_db


# =============================================================================
# COMPANY MODEL TESTS
# =============================================================================

class TestCompanyModel:
    """Tests for Company model."""
    
    def test_create_company_with_valid_uen(self):
        """Test company creation with valid Singapore UEN."""
        company = CompanyFactory(uen='201812345A')
        assert company.id is not None
        assert company.uen == '201812345A'
    
    def test_company_str_representation(self):
        """Test string representation of company."""
        company = CompanyFactory(name='Test Corp', uen='201812345A')
        assert str(company) == 'Test Corp (201812345A)'
    
    def test_uen_uniqueness(self):
        """Test that duplicate UEN raises error."""
        CompanyFactory(uen='201812345A')
        
        with pytest.raises(Exception):  # IntegrityError
            CompanyFactory(uen='201812345A')
    
    def test_gst_registered_company(self):
        """Test GST-registered company properties."""
        company = GSTRegisteredCompanyFactory()
        assert company.gst_registered is True
        assert company.is_gst_registered is True
        assert company.gst_registration_number != ''
    
    def test_non_gst_registered_company(self):
        """Test non-GST-registered company."""
        company = CompanyFactory(gst_registered=False)
        assert company.is_gst_registered is False
    
    def test_company_settings_json(self):
        """Test company settings JSON field."""
        company = CompanyFactory()
        company.set_setting('theme', 'dark')
        
        assert company.get_setting('theme') == 'dark'
        assert company.get_setting('nonexistent', 'default') == 'default'
    
    def test_soft_delete(self):
        """Test soft delete functionality."""
        company = CompanyFactory()
        company_id = company.id
        
        company.delete()
        
        # Should not appear in default queryset
        assert Company.objects.filter(id=company_id).count() == 0
        
        # Should appear in all_objects
        assert Company.all_objects.filter(id=company_id).count() == 1
        assert Company.all_objects.get(id=company_id).is_deleted is True


# =============================================================================
# USER MODEL TESTS
# =============================================================================

class TestUserModel:
    """Tests for User model."""
    
    def test_create_user_with_email(self):
        """Test user creation with email as identifier."""
        user = UserFactory(email='test@example.com')
        assert user.id is not None
        assert user.email == 'test@example.com'
    
    def test_user_str_representation(self):
        """Test string representation of user."""
        user = UserFactory(email='test@example.com')
        assert str(user) == 'test@example.com'
    
    def test_user_full_name(self):
        """Test full name property."""
        user = UserFactory(first_name='John', last_name='Doe')
        assert user.full_name == 'John Doe'
    
    def test_user_full_name_fallback_to_email(self):
        """Test full name falls back to email when names empty."""
        user = UserFactory(first_name='', last_name='', email='test@example.com')
        assert user.full_name == 'test@example.com'
    
    def test_user_company_association(self):
        """Test user belongs to company."""
        company = CompanyFactory()
        user = UserFactory(company=company)
        
        assert user.company == company
        assert user in company.users.all()
    
    def test_email_uniqueness(self):
        """Test that duplicate email raises error."""
        UserFactory(email='duplicate@example.com')
        
        with pytest.raises(Exception):
            UserFactory(email='duplicate@example.com')
    
    def test_password_authentication(self):
        """Test password check."""
        user = UserFactory()
        user.set_password('securepass123')
        user.save()
        
        assert user.check_password('securepass123') is True
        assert user.check_password('wrongpass') is False
    
    def test_record_failed_login(self):
        """Test failed login attempt recording."""
        user = UserFactory(failed_login_attempts=0)
        
        user.record_failed_login()
        
        assert user.failed_login_attempts == 1
    
    def test_account_lockout_after_failed_attempts(self):
        """Test account locks after 5 failed attempts."""
        user = UserFactory(failed_login_attempts=4)
        
        user.record_failed_login()
        
        assert user.failed_login_attempts == 5
        assert user.locked_until is not None
        assert user.is_locked is True
    
    def test_successful_login_resets_failed_attempts(self):
        """Test successful login resets failed attempts."""
        user = UserFactory(failed_login_attempts=3)
        
        user.record_successful_login('127.0.0.1')
        
        assert user.failed_login_attempts == 0
        assert user.locked_until is None
        assert user.last_login_ip == '127.0.0.1'
    
    def test_create_superuser(self):
        """Test superuser creation."""
        user = SuperUserFactory()
        
        assert user.is_staff is True
        assert user.is_superuser is True


# =============================================================================
# ROLE MODEL TESTS
# =============================================================================

class TestRoleModel:
    """Tests for Role model."""
    
    def test_create_role(self):
        """Test role creation."""
        role = RoleFactory(name='test_role')
        assert role.id is not None
        assert role.name == 'test_role'
    
    def test_role_str_representation(self):
        """Test string representation of role."""
        company = CompanyFactory(name='Test Corp')
        role = RoleFactory(name='admin', company=company)
        assert str(role) == 'admin (Test Corp)'
    
    def test_role_permissions_check(self):
        """Test role permission checking."""
        role = RoleFactory(permissions=['users.view', 'orders.create'])
        
        assert role.has_permission('users.view') is True
        assert role.has_permission('orders.create') is True
        assert role.has_permission('products.delete') is False
    
    def test_owner_role_has_all_permissions(self):
        """Test owner role with 'all' permission."""
        role = OwnerRoleFactory()
        
        assert role.has_permission('anything') is True
        assert role.has_permission('products.delete') is True
    
    def test_add_permission_to_role(self):
        """Test adding permission to role."""
        role = RoleFactory(permissions=['users.view'])
        
        role.add_permission('users.create')
        
        assert 'users.create' in role.permissions
    
    def test_remove_permission_from_role(self):
        """Test removing permission from role."""
        role = RoleFactory(permissions=['users.view', 'users.create'])
        
        role.remove_permission('users.create')
        
        assert 'users.create' not in role.permissions


# =============================================================================
# USER ROLE MODEL TESTS
# =============================================================================

class TestUserRoleModel:
    """Tests for UserRole model."""
    
    def test_assign_role_to_user(self):
        """Test role assignment to user."""
        company = CompanyFactory()
        user = UserFactory(company=company)
        role = RoleFactory(company=company)
        
        user_role = UserRoleFactory(user=user, role=role)
        
        assert user_role.user == user
        assert user_role.role == role
        assert user_role.assigned_at is not None
    
    def test_user_roles_property(self):
        """Test user roles property."""
        company = CompanyFactory()
        user = UserFactory(company=company)
        role1 = RoleFactory(company=company, name='role1')
        role2 = RoleFactory(company=company, name='role2')
        
        UserRoleFactory(user=user, role=role1)
        UserRoleFactory(user=user, role=role2)
        
        user_roles = list(user.roles.values_list('name', flat=True))
        assert 'role1' in user_roles
        assert 'role2' in user_roles
    
    def test_unique_user_role_constraint(self):
        """Test that same role can't be assigned twice."""
        company = CompanyFactory()
        user = UserFactory(company=company)
        role = RoleFactory(company=company)
        
        UserRoleFactory(user=user, role=role)
        
        with pytest.raises(Exception):  # IntegrityError
            UserRoleFactory(user=user, role=role)

```

# backend/apps/accounts/admin.py
```py
"""
Django Admin configuration for accounts app.

Provides admin interfaces for:
- Company management
- User management
- Role management
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import Company, User, Role, UserRole


# =============================================================================
# INLINE ADMINS
# =============================================================================

class UserRoleInline(admin.TabularInline):
    """Inline for managing user role assignments."""
    model = UserRole
    extra = 1
    autocomplete_fields = ['role']
    readonly_fields = ['assigned_at', 'assigned_by']


class CompanyUserInline(admin.TabularInline):
    """Inline for viewing company users."""
    model = User
    extra = 0
    fields = ['email', 'first_name', 'last_name', 'is_active']
    readonly_fields = ['email']
    can_delete = False
    max_num = 0  # Don't allow adding users inline


class CompanyRoleInline(admin.TabularInline):
    """Inline for managing company roles."""
    model = Role
    extra = 0
    fields = ['name', 'description', 'is_system']
    readonly_fields = ['is_system']


# =============================================================================
# COMPANY ADMIN
# =============================================================================

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Admin interface for Company model."""
    
    list_display = [
        'name', 'uen', 'gst_status', 'plan_tier', 'user_count', 'created_at'
    ]
    list_filter = ['gst_registered', 'plan_tier', 'created_at']
    search_fields = ['name', 'uen', 'email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'legal_name', 'uen')
        }),
        ('GST Information', {
            'fields': ('gst_registered', 'gst_registration_number', 'gst_registration_date'),
            'classes': ('collapse',)
        }),
        ('Contact', {
            'fields': ('email', 'phone', 'website')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'postal_code'),
            'classes': ('collapse',)
        }),
        ('Subscription', {
            'fields': ('plan_tier', 'settings')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [CompanyRoleInline, CompanyUserInline]
    
    def gst_status(self, obj):
        """Display GST registration status with color."""
        if obj.gst_registered:
            return format_html(
                '<span style="color: green;">✓ {}</span>',
                obj.gst_registration_number
            )
        return format_html('<span style="color: gray;">Not Registered</span>')
    gst_status.short_description = 'GST Status'
    
    def user_count(self, obj):
        """Display count of users."""
        return obj.users.count()
    user_count.short_description = 'Users'


# =============================================================================
# USER ADMIN
# =============================================================================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model (email-based)."""
    
    list_display = [
        'email', 'full_name', 'company', 'is_active', 'is_verified', 'mfa_status', 'last_login'
    ]
    list_filter = ['is_active', 'is_verified', 'is_staff', 'mfa_enabled', 'company']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    # Override fieldsets for email-based user
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone')
        }),
        ('Company', {
            'fields': ('company',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified')
        }),
        ('Security', {
            'fields': ('mfa_enabled', 'failed_login_attempts', 'locked_until', 'last_login_ip'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'company'),
        }),
    )
    
    readonly_fields = ['last_login', 'created_at', 'updated_at', 'last_login_ip']
    autocomplete_fields = ['company']
    inlines = [UserRoleInline]
    
    def full_name(self, obj):
        """Display user's full name."""
        return obj.full_name
    full_name.short_description = 'Name'
    
    def mfa_status(self, obj):
        """Display MFA status with icon."""
        if obj.mfa_enabled:
            return format_html('<span style="color: green;">✓ Enabled</span>')
        return format_html('<span style="color: gray;">Disabled</span>')
    mfa_status.short_description = 'MFA'


# =============================================================================
# ROLE ADMIN
# =============================================================================

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin interface for Role model."""
    
    list_display = ['name', 'company', 'permission_count', 'user_count', 'is_system']
    list_filter = ['is_system', 'company']
    search_fields = ['name', 'description']
    ordering = ['company', 'name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'company')
        }),
        ('Permissions', {
            'fields': ('permissions',),
            'description': 'Enter permissions as a JSON array, e.g. ["users.view", "orders.create"]'
        }),
        ('System', {
            'fields': ('is_system',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['is_system']
    
    def permission_count(self, obj):
        """Display count of permissions."""
        if 'all' in obj.permissions:
            return 'All'
        return len(obj.permissions)
    permission_count.short_description = 'Permissions'
    
    def user_count(self, obj):
        """Display count of users with this role."""
        return obj.user_roles.count()
    user_count.short_description = 'Users'


# =============================================================================
# USER ROLE ADMIN
# =============================================================================

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Admin interface for user-role assignments."""
    
    list_display = ['user', 'role', 'assigned_at', 'assigned_by']
    list_filter = ['role', 'assigned_at']
    search_fields = ['user__email', 'role__name']
    ordering = ['-assigned_at']
    autocomplete_fields = ['user', 'role', 'assigned_by']
    readonly_fields = ['assigned_at']


# =============================================================================
# ADMIN SITE CUSTOMIZATION
# =============================================================================

admin.site.site_header = 'Singapore SMB Platform'
admin.site.site_title = 'SMB Admin'
admin.site.index_title = 'Platform Administration'

```

# backend/apps/accounts/serializers.py
```py
"""
DRF Serializers for accounts app.

Provides serialization for:
- Company: Company CRUD operations
- User: User management and profile
- Role: Role management
- Authentication: Login, token handling
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import Company, User, Role, UserRole


# =============================================================================
# COMPANY SERIALIZERS
# =============================================================================

class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Company CRUD operations."""
    
    is_gst_registered = serializers.BooleanField(read_only=True)
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'legal_name', 'uen',
            'gst_registered', 'gst_registration_number', 'gst_registration_date',
            'is_gst_registered',
            'email', 'phone', 'website',
            'address_line1', 'address_line2', 'postal_code',
            'plan_tier', 'settings',
            'user_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user_count(self, obj):
        """Get count of users in this company."""
        return obj.users.count()
    
    def validate_uen(self, value):
        """Validate Singapore UEN format."""
        import re
        if not re.match(r'^[0-9]{8,9}[A-Za-z]$', value):
            raise serializers.ValidationError(
                'Invalid UEN format. Example: 201812345A'
            )
        return value.upper()


class CompanyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new company with owner."""
    
    owner_email = serializers.EmailField(write_only=True)
    owner_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    owner_first_name = serializers.CharField(write_only=True, required=False)
    owner_last_name = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Company
        fields = [
            'name', 'legal_name', 'uen',
            'gst_registered', 'gst_registration_number',
            'email', 'phone',
            'address_line1', 'postal_code',
            'owner_email', 'owner_password', 'owner_first_name', 'owner_last_name',
        ]
    
    def validate_owner_password(self, value):
        """Validate password strength."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def create(self, validated_data):
        """Create company with owner user."""
        owner_email = validated_data.pop('owner_email')
        owner_password = validated_data.pop('owner_password')
        owner_first_name = validated_data.pop('owner_first_name', '')
        owner_last_name = validated_data.pop('owner_last_name', '')
        
        # Create company
        company = Company.objects.create(**validated_data)
        
        # Create owner user
        user = User.objects.create_user(
            email=owner_email,
            password=owner_password,
            company=company,
            first_name=owner_first_name,
            last_name=owner_last_name,
            is_verified=True,
        )
        
        # Assign owner role
        owner_role, _ = Role.objects.get_or_create(
            company=company,
            name='owner',
            defaults={
                'description': 'Company owner with full access',
                'permissions': ['all'],
            }
        )
        UserRole.objects.create(user=user, role=owner_role)
        
        return company


# =============================================================================
# USER SERIALIZERS
# =============================================================================

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User read operations."""
    
    full_name = serializers.CharField(read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    roles_list = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'company', 'company_name',
            'is_active', 'is_verified', 'mfa_enabled',
            'roles_list',
            'last_login', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'email', 'company', 'last_login', 'created_at', 'updated_at']
    
    def get_roles_list(self, obj):
        """Get list of role names."""
        return list(obj.roles.values_list('name', flat=True))


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""
    
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})
    role_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        default=list
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone',
            'role_ids',
        ]
    
    def validate(self, data):
        """Validate passwords match."""
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        return data
    
    def validate_password(self, value):
        """Validate password strength."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def create(self, validated_data):
        """Create user with role assignments."""
        validated_data.pop('password_confirm')
        role_ids = validated_data.pop('role_ids', [])
        password = validated_data.pop('password')
        
        # Get company from context (set by view)
        company = self.context.get('company')
        
        user = User.objects.create_user(
            password=password,
            company=company,
            **validated_data
        )
        
        # Assign roles
        for role_id in role_ids:
            try:
                role = Role.objects.get(id=role_id, company=company)
                UserRole.objects.create(user=user, role=role)
            except Role.DoesNotExist:
                pass
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone']


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing password."""
    
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_current_password(self, value):
        """Verify current password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value
    
    def validate(self, data):
        """Validate new passwords match and strength."""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Passwords do not match.'
            })
        
        try:
            validate_password(data['new_password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
        
        return data


# =============================================================================
# ROLE SERIALIZERS
# =============================================================================

class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role CRUD operations."""
    
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'description', 'permissions',
            'is_system', 'user_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'is_system', 'created_at', 'updated_at']
    
    def get_user_count(self, obj):
        """Get count of users with this role."""
        return obj.user_roles.count()


class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer for user-role assignments."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    
    class Meta:
        model = UserRole
        fields = ['id', 'user', 'user_email', 'role', 'role_name', 'assigned_at']
        read_only_fields = ['id', 'assigned_at']


# =============================================================================
# AUTHENTICATION SERIALIZERS
# =============================================================================

class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, data):
        """Authenticate user."""
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password
            )
            
            if not user:
                # Check if user exists and is locked
                try:
                    existing_user = User.objects.get(email=email)
                    if existing_user.is_locked:
                        raise serializers.ValidationError({
                            'non_field_errors': ['Account is locked. Try again later.']
                        })
                    existing_user.record_failed_login()
                except User.DoesNotExist:
                    pass
                
                raise serializers.ValidationError({
                    'non_field_errors': ['Invalid email or password.']
                })
            
            if not user.is_active:
                raise serializers.ValidationError({
                    'non_field_errors': ['Account is disabled.']
                })
            
            data['user'] = user
        else:
            raise serializers.ValidationError({
                'non_field_errors': ['Email and password are required.']
            })
        
        return data


class TokenSerializer(serializers.Serializer):
    """Serializer for JWT token response."""
    
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer(read_only=True)


class TokenRefreshSerializer(serializers.Serializer):
    """Serializer for token refresh."""
    
    refresh = serializers.CharField()

```

# backend/apps/accounts/services.py
```py
"""
Business logic services for accounts app.

Provides:
- AuthService: Authentication and token management
- UserService: User management operations
- CompanyService: Company management operations
"""
from typing import Optional, Tuple
from datetime import timedelta

from django.utils import timezone
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Company, User, Role, UserRole


class AuthService:
    """
    Service for authentication and token management.
    
    Handles:
    - User authentication
    - JWT token generation
    - Token refresh
    - Login tracking
    """
    
    @staticmethod
    def authenticate(email: str, password: str, ip_address: str = None) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User's email address
            password: User's password
            ip_address: Client IP for tracking
        
        Returns:
            User if authentication successful, None otherwise
        """
        try:
            user = User.objects.get(email=email.lower())
        except User.DoesNotExist:
            return None
        
        # Check if account is locked
        if user.is_locked:
            return None
        
        # Check password
        if not user.check_password(password):
            user.record_failed_login()
            return None
        
        # Check if active
        if not user.is_active:
            return None
        
        # Record successful login
        user.record_successful_login(ip_address)
        
        return user
    
    @staticmethod
    def generate_tokens(user: User) -> dict:
        """
        Generate JWT access and refresh tokens for user.
        
        Args:
            user: Authenticated user
        
        Returns:
            Dict with 'access' and 'refresh' tokens
        """
        refresh = RefreshToken.for_user(user)
        
        # Add custom claims
        refresh['email'] = user.email
        if user.company:
            refresh['company_id'] = str(user.company.id)
        
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
    
    @staticmethod
    def refresh_token(refresh_token: str) -> dict:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            Dict with new 'access' token
        
        Raises:
            Exception if refresh token is invalid
        """
        refresh = RefreshToken(refresh_token)
        
        return {
            'access': str(refresh.access_token),
        }
    
    @staticmethod
    def blacklist_token(refresh_token: str) -> bool:
        """
        Blacklist a refresh token (logout).
        
        Args:
            refresh_token: Token to blacklist
        
        Returns:
            True if successful
        """
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return True
        except Exception:
            return False


class UserService:
    """
    Service for user management operations.
    
    Handles:
    - User creation
    - User updates
    - Role assignment
    - Password management
    """
    
    @staticmethod
    @transaction.atomic
    def create_user(
        email: str,
        password: str,
        company: Company,
        first_name: str = '',
        last_name: str = '',
        phone: str = '',
        role_names: list = None,
        created_by: User = None
    ) -> User:
        """
        Create a new user with optional role assignment.
        
        Args:
            email: User's email
            password: User's password
            company: Company to associate user with
            first_name: Optional first name
            last_name: Optional last name
            phone: Optional phone number
            role_names: List of role names to assign
            created_by: User creating this user
        
        Returns:
            Created User instance
        """
        user = User.objects.create_user(
            email=email.lower(),
            password=password,
            company=company,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        )
        
        # Assign roles
        if role_names:
            for role_name in role_names:
                try:
                    role = Role.objects.get(name=role_name, company=company)
                    UserRole.objects.create(
                        user=user,
                        role=role,
                        assigned_by=created_by
                    )
                except Role.DoesNotExist:
                    pass
        
        return user
    
    @staticmethod
    def update_user(user: User, **kwargs) -> User:
        """
        Update user profile fields.
        
        Args:
            user: User to update
            **kwargs: Fields to update
        
        Returns:
            Updated User instance
        """
        allowed_fields = ['first_name', 'last_name', 'phone']
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(user, field, value)
        
        user.save()
        return user
    
    @staticmethod
    def change_password(user: User, new_password: str) -> User:
        """
        Change user's password.
        
        Args:
            user: User to update
            new_password: New password
        
        Returns:
            Updated User instance
        """
        user.set_password(new_password)
        user.save()
        return user
    
    @staticmethod
    @transaction.atomic
    def assign_role(user: User, role: Role, assigned_by: User = None) -> UserRole:
        """
        Assign a role to a user.
        
        Args:
            user: User to assign role to
            role: Role to assign
            assigned_by: User assigning the role
        
        Returns:
            Created UserRole instance
        """
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=role,
            defaults={'assigned_by': assigned_by}
        )
        return user_role
    
    @staticmethod
    def remove_role(user: User, role: Role) -> bool:
        """
        Remove a role from a user.
        
        Args:
            user: User to remove role from
            role: Role to remove
        
        Returns:
            True if role was removed
        """
        deleted, _ = UserRole.objects.filter(user=user, role=role).delete()
        return deleted > 0
    
    @staticmethod
    def has_permission(user: User, permission: str) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            user: User to check
            permission: Permission string to check
        
        Returns:
            True if user has the permission
        """
        if user.is_superuser:
            return True
        
        for role in user.roles:
            if role.has_permission(permission):
                return True
        
        return False


class CompanyService:
    """
    Service for company management operations.
    
    Handles:
    - Company creation with owner
    - Company settings
    - Default role creation
    """
    
    DEFAULT_ROLES = [
        {
            'name': 'owner',
            'description': 'Company owner with full access',
            'permissions': ['all'],
        },
        {
            'name': 'admin',
            'description': 'Administrative access',
            'permissions': [
                'users.view', 'users.create', 'users.update', 'users.delete',
                'products.view', 'products.create', 'products.update', 'products.delete',
                'orders.view', 'orders.update',
                'inventory.view', 'inventory.update',
                'settings.view', 'settings.update',
            ],
        },
        {
            'name': 'finance',
            'description': 'Financial operations',
            'permissions': [
                'orders.view', 'invoices.view', 'invoices.create',
                'payments.view', 'reports.view',
                'gst.view', 'gst.submit',
            ],
        },
        {
            'name': 'warehouse',
            'description': 'Inventory management',
            'permissions': [
                'products.view', 'inventory.view', 'inventory.update',
                'orders.view', 'orders.fulfill',
            ],
        },
        {
            'name': 'sales',
            'description': 'Sales operations',
            'permissions': [
                'products.view', 'customers.view', 'customers.create',
                'orders.view', 'orders.create',
            ],
        },
    ]
    
    @staticmethod
    @transaction.atomic
    def create_company(
        name: str,
        uen: str,
        email: str,
        owner_email: str,
        owner_password: str,
        **company_kwargs
    ) -> Tuple[Company, User]:
        """
        Create a new company with owner and default roles.
        
        Args:
            name: Company name
            uen: Singapore UEN
            email: Company contact email
            owner_email: Owner's email
            owner_password: Owner's password
            **company_kwargs: Additional company fields
        
        Returns:
            Tuple of (Company, owner User)
        """
        # Create company
        company = Company.objects.create(
            name=name,
            uen=uen.upper(),
            email=email,
            **company_kwargs
        )
        
        # Create default roles
        CompanyService.create_default_roles(company)
        
        # Create owner user
        owner = User.objects.create_user(
            email=owner_email.lower(),
            password=owner_password,
            company=company,
            is_verified=True,
        )
        
        # Assign owner role
        owner_role = Role.objects.get(company=company, name='owner')
        UserRole.objects.create(user=owner, role=owner_role)
        
        return company, owner
    
    @staticmethod
    def create_default_roles(company: Company) -> list:
        """
        Create default roles for a company.
        
        Args:
            company: Company to create roles for
        
        Returns:
            List of created Role instances
        """
        roles = []
        for role_data in CompanyService.DEFAULT_ROLES:
            role, created = Role.objects.get_or_create(
                company=company,
                name=role_data['name'],
                defaults={
                    'description': role_data['description'],
                    'permissions': role_data['permissions'],
                }
            )
            roles.append(role)
        return roles
    
    @staticmethod
    def check_gst_threshold(company: Company, annual_revenue: float) -> bool:
        """
        Check if company should register for GST.
        
        Singapore GST registration is required if annual revenue >= S$1,000,000.
        
        Args:
            company: Company to check
            annual_revenue: Annual revenue in SGD
        
        Returns:
            True if GST registration is required
        """
        from decimal import Decimal
        from django.conf import settings
        
        threshold = getattr(settings, 'GST_REGISTRATION_THRESHOLD', Decimal('1000000'))
        return Decimal(str(annual_revenue)) >= threshold

```

# backend/apps/accounts/models.py
```py
"""
Models for accounts app.

This module defines:
- Company: Multi-tenant root entity (Singapore business with UEN)
- User: Custom user model with email-based authentication
- Role: RBAC roles with JSON-based permissions
- UserRole: Junction table for user-role assignments
"""
import re
import uuid
from decimal import Decimal

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import RegexValidator
from django.utils import timezone

from core.models import BaseModel, SoftDeleteModel


# =============================================================================
# VALIDATORS
# =============================================================================

uen_validator = RegexValidator(
    regex=r'^[0-9]{8,9}[A-Za-z]$',
    message='Enter a valid Singapore UEN (e.g., 201812345A)'
)

phone_validator = RegexValidator(
    regex=r'^\+?[0-9]{8,15}$',
    message='Enter a valid phone number'
)


# =============================================================================
# COMPANY MODEL
# =============================================================================

class Company(SoftDeleteModel):
    """
    Company entity - the root of multi-tenant data isolation.
    
    Represents a Singapore business registered with ACRA.
    All business data (products, orders, etc.) belongs to a Company.
    
    Attributes:
        uen: Singapore Unique Entity Number (required, unique)
        gst_registered: Whether company is GST-registered
        settings: JSON field for company-specific configurations
    """
    
    class PlanTier(models.TextChoices):
        LITE = 'lite', 'Lite (Free)'
        STANDARD = 'standard', 'Standard'
        ADVANCED = 'advanced', 'Advanced'
    
    # Basic Information
    name = models.CharField(
        max_length=200,
        help_text="Trading name"
    )
    legal_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Registered legal name"
    )
    uen = models.CharField(
        max_length=10,
        unique=True,
        validators=[uen_validator],
        help_text="Singapore Unique Entity Number (e.g., 201812345A)"
    )
    
    # GST Information
    gst_registered = models.BooleanField(
        default=False,
        help_text="Is the company registered for GST?"
    )
    gst_registration_number = models.CharField(
        max_length=15,
        blank=True,
        help_text="GST registration number (if registered)"
    )
    gst_registration_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of GST registration"
    )
    
    # Contact Information
    email = models.EmailField(
        help_text="Primary contact email"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[phone_validator],
        help_text="Primary contact phone"
    )
    website = models.URLField(
        blank=True,
        help_text="Company website URL"
    )
    
    # Address
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(
        max_length=6,
        blank=True,
        help_text="Singapore postal code (6 digits)"
    )
    
    # Subscription
    plan_tier = models.CharField(
        max_length=20,
        choices=PlanTier.choices,
        default=PlanTier.LITE,
        help_text="Subscription plan tier"
    )
    
    # Settings (JSONB for flexibility)
    settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Company-specific settings"
    )
    
    class Meta:
        db_table = 'core_companies'
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['name']
        indexes = [
            models.Index(fields=['uen']),
            models.Index(fields=['gst_registered']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.uen})"
    
    @property
    def is_gst_registered(self) -> bool:
        """Check if company is currently GST registered."""
        return self.gst_registered and bool(self.gst_registration_number)
    
    def get_setting(self, key: str, default=None):
        """Get a setting value from the settings JSON."""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value):
        """Set a setting value in the settings JSON."""
        self.settings[key] = value
        self.save(update_fields=['settings', 'updated_at'])


# =============================================================================
# USER MANAGER
# =============================================================================

class UserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError('Email is required')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


# =============================================================================
# USER MODEL
# =============================================================================

class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    Custom user model with email-based authentication.
    
    Uses email instead of username for authentication.
    Associated with a Company for multi-tenant isolation.
    
    Attributes:
        email: Primary identifier (unique)
        company: Associated company (optional for superusers)
        mfa_enabled: Whether MFA is enabled for this user
    """
    
    # Authentication
    email = models.EmailField(
        unique=True,
        help_text="Email address (used for login)"
    )
    
    # Company association (null for superusers)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='users',
        help_text="Company this user belongs to"
    )
    
    # Profile
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[phone_validator]
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether user can log in"
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Can access admin site"
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Email has been verified"
    )
    
    # Security
    mfa_enabled = models.BooleanField(
        default=False,
        help_text="Multi-factor authentication enabled"
    )
    mfa_secret = models.CharField(
        max_length=32,
        blank=True,
        help_text="TOTP secret for MFA"
    )
    failed_login_attempts = models.PositiveIntegerField(
        default=0,
        help_text="Number of consecutive failed login attempts"
    )
    locked_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Account locked until this time"
    )
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of last login"
    )
    
    # Manager
    objects = UserManager()
    
    # Authentication settings
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email is already required via USERNAME_FIELD
    
    class Meta:
        db_table = 'core_users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['email']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['company']),
        ]
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        name = f"{self.first_name} {self.last_name}".strip()
        return name or self.email
    
    @property
    def is_locked(self) -> bool:
        """Check if account is currently locked."""
        if self.locked_until is None:
            return False
        return timezone.now() < self.locked_until
    
    def record_failed_login(self):
        """Record a failed login attempt."""
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.locked_until = timezone.now() + timezone.timedelta(minutes=30)
        
        self.save(update_fields=['failed_login_attempts', 'locked_until', 'updated_at'])
    
    def record_successful_login(self, ip_address=None):
        """Record a successful login."""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.last_login = timezone.now()
        self.last_login_ip = ip_address
        self.save(update_fields=[
            'failed_login_attempts', 'locked_until', 
            'last_login', 'last_login_ip', 'updated_at'
        ])


# =============================================================================
# ROLE MODEL
# =============================================================================

class Role(BaseModel):
    """
    Role for RBAC (Role-Based Access Control).
    
    Permissions are stored as a JSON array of permission strings.
    Each company can have its own custom roles.
    
    Built-in roles (is_system=True):
    - owner: Full access
    - admin: Administrative access
    - finance: Financial operations
    - warehouse: Inventory management
    - sales: Sales and customer management
    """
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='roles',
        help_text="Company this role belongs to (null for system roles)"
    )
    
    name = models.CharField(
        max_length=50,
        help_text="Role name (e.g., 'admin', 'finance')"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of this role"
    )
    
    # Permissions as JSON array
    permissions = models.JSONField(
        default=list,
        blank=True,
        help_text="List of permission strings"
    )
    
    # System flag
    is_system = models.BooleanField(
        default=False,
        help_text="Whether this is a built-in system role"
    )
    
    class Meta:
        db_table = 'core_roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'name'],
                name='unique_role_per_company'
            )
        ]
    
    def __str__(self):
        if self.company:
            return f"{self.name} ({self.company.name})"
        return f"{self.name} (System)"
    
    def has_permission(self, permission: str) -> bool:
        """Check if this role has a specific permission."""
        if 'all' in self.permissions:
            return True
        return permission in self.permissions
    
    def add_permission(self, permission: str):
        """Add a permission to this role."""
        if permission not in self.permissions:
            self.permissions.append(permission)
            self.save(update_fields=['permissions', 'updated_at'])
    
    def remove_permission(self, permission: str):
        """Remove a permission from this role."""
        if permission in self.permissions:
            self.permissions.remove(permission)
            self.save(update_fields=['permissions', 'updated_at'])


# =============================================================================
# USER-ROLE JUNCTION
# =============================================================================

class UserRole(BaseModel):
    """
    Junction table for User-Role many-to-many relationship.
    
    Tracks when role was assigned and by whom.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='roles_assigned',
        help_text="User who assigned this role"
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this role was assigned"
    )
    
    class Meta:
        db_table = 'core_user_roles'
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'role'],
                name='unique_user_role'
            )
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.role.name}"


# =============================================================================
# ADD ROLES RELATION TO USER
# =============================================================================

# Add a property to User for easy role access
User.add_to_class(
    'roles',
    property(lambda self: Role.objects.filter(user_roles__user=self))
)

```

# backend/apps/accounts/views.py
```py
"""
DRF Views for accounts app.

Provides ViewSets and APIViews for:
- Company management
- User management
- Role management
- Authentication (login, logout, token refresh)
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from core.permissions import IsCompanyMember, IsAdminUser, HasAnyRole
from .models import Company, User, Role, UserRole
from .serializers import (
    CompanySerializer, CompanyCreateSerializer,
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    PasswordChangeSerializer,
    RoleSerializer, UserRoleSerializer,
    LoginSerializer, TokenSerializer, TokenRefreshSerializer,
)
from .services import AuthService, UserService, CompanyService


# =============================================================================
# COMPANY VIEWSET
# =============================================================================

class CompanyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Company CRUD operations.
    
    list: List companies (admin only)
    create: Create new company with owner
    retrieve: Get company details
    update: Update company
    """
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return companies based on user access."""
        user = self.request.user
        
        if user.is_superuser:
            return Company.objects.all()
        
        # Regular users can only see their own company
        if user.company:
            return Company.objects.filter(id=user.company.id)
        
        return Company.objects.none()
    
    def get_serializer_class(self):
        """Use different serializer for create."""
        if self.action == 'create':
            return CompanyCreateSerializer
        return CompanySerializer
    
    def get_permissions(self):
        """Allow unauthenticated company creation (registration)."""
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Get all users in the company."""
        company = self.get_object()
        users = company.users.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def roles(self, request, pk=None):
        """Get all roles in the company."""
        company = self.get_object()
        roles = company.roles.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)


# =============================================================================
# USER VIEWSET
# =============================================================================

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User CRUD operations.
    
    Filtered by company for multi-tenant isolation.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    
    def get_queryset(self):
        """Return users in the current company."""
        user = self.request.user
        
        if user.is_superuser:
            return User.objects.all()
        
        if user.company:
            return User.objects.filter(company=user.company, is_active=True)
        
        return User.objects.none()
    
    def get_serializer_class(self):
        """Use different serializers based on action."""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_serializer_context(self):
        """Add company to serializer context."""
        context = super().get_serializer_context()
        if self.request.user.is_authenticated:
            context['company'] = self.request.user.company
        return context
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'])
    def update_profile(self, request):
        """Update current user's profile."""
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change current user's password."""
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        UserService.change_password(
            request.user,
            serializer.validated_data['new_password']
        )
        
        return Response({'message': 'Password changed successfully.'})
    
    @action(detail=True, methods=['post'])
    def assign_role(self, request, pk=None):
        """Assign a role to a user."""
        user = self.get_object()
        role_id = request.data.get('role_id')
        
        try:
            role = Role.objects.get(id=role_id, company=request.user.company)
        except Role.DoesNotExist:
            return Response(
                {'error': 'Role not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        UserService.assign_role(user, role, request.user)
        return Response({'message': f'Role {role.name} assigned.'})
    
    @action(detail=True, methods=['post'])
    def remove_role(self, request, pk=None):
        """Remove a role from a user."""
        user = self.get_object()
        role_id = request.data.get('role_id')
        
        try:
            role = Role.objects.get(id=role_id, company=request.user.company)
        except Role.DoesNotExist:
            return Response(
                {'error': 'Role not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        UserService.remove_role(user, role)
        return Response({'message': f'Role {role.name} removed.'})


# =============================================================================
# ROLE VIEWSET
# =============================================================================

class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Role CRUD operations.
    
    Only admins can manage roles.
    """
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    
    def get_queryset(self):
        """Return roles for the current company."""
        user = self.request.user
        
        if user.is_superuser:
            return Role.objects.all()
        
        if user.company:
            return Role.objects.filter(company=user.company)
        
        return Role.objects.none()
    
    def perform_create(self, serializer):
        """Set company when creating role."""
        serializer.save(company=self.request.user.company)
    
    def destroy(self, request, *args, **kwargs):
        """Prevent deletion of system roles."""
        role = self.get_object()
        if role.is_system:
            return Response(
                {'error': 'Cannot delete system roles.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


# =============================================================================
# AUTHENTICATION VIEWS
# =============================================================================

class LoginView(APIView):
    """
    User login endpoint.
    
    POST /api/v1/accounts/auth/login/
    
    Request Body:
        email: User's email
        password: User's password
    
    Response:
        access: JWT access token
        refresh: JWT refresh token
        user: User details
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Get client IP
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            ip_address = ip_address.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Record login and generate tokens
        user.record_successful_login(ip_address)
        tokens = AuthService.generate_tokens(user)
        
        return Response({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': UserSerializer(user).data,
        })


class LogoutView(APIView):
    """
    User logout endpoint.
    
    POST /api/v1/accounts/auth/logout/
    
    Request Body:
        refresh: JWT refresh token to blacklist
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        refresh_token = request.data.get('refresh')
        
        if refresh_token:
            AuthService.blacklist_token(refresh_token)
        
        return Response({'message': 'Logged out successfully.'})


class TokenRefreshView(APIView):
    """
    Token refresh endpoint.
    
    POST /api/v1/accounts/auth/refresh/
    
    Request Body:
        refresh: JWT refresh token
    
    Response:
        access: New JWT access token
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tokens = AuthService.refresh_token(refresh_token)
            return Response(tokens)
        except (InvalidToken, TokenError) as e:
            return Response(
                {'error': 'Invalid or expired token.'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class CurrentUserView(APIView):
    """
    Get current authenticated user.
    
    GET /api/v1/accounts/auth/me/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response(UserSerializer(request.user).data)

```

# backend/apps/accounts/urls.py
```py
"""
URL routing for accounts app.

API Endpoints:
- /api/v1/accounts/companies/ - Company CRUD
- /api/v1/accounts/users/ - User CRUD
- /api/v1/accounts/roles/ - Role CRUD
- /api/v1/accounts/auth/login/ - Login
- /api/v1/accounts/auth/logout/ - Logout
- /api/v1/accounts/auth/refresh/ - Token refresh
- /api/v1/accounts/auth/me/ - Current user
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CompanyViewSet, UserViewSet, RoleViewSet,
    LoginView, LogoutView, TokenRefreshView, CurrentUserView,
)

app_name = 'accounts'

# Router for ViewSets
router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')

# URL patterns
urlpatterns = [
    # ViewSet routes
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/me/', CurrentUserView.as_view(), name='current-user'),
]

```

# backend/apps/__init__.py
```py
"""Apps package for Singapore SMB E-commerce Platform."""

```

# backend/uv.lock
```lock
version = 1
revision = 3
requires-python = ">=3.12"
resolution-markers = [
    "python_full_version >= '3.13'",
    "python_full_version < '3.13'",
]

[[package]]
name = "amqp"
version = "5.3.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "vine" },
]
sdist = { url = "https://files.pythonhosted.org/packages/79/fc/ec94a357dfc6683d8c86f8b4cfa5416a4c36b28052ec8260c77aca96a443/amqp-5.3.1.tar.gz", hash = "sha256:cddc00c725449522023bad949f70fff7b48f0b1ade74d170a6f10ab044739432", size = 129013, upload-time = "2024-11-12T19:55:44.051Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/26/99/fc813cd978842c26c82534010ea849eee9ab3a13ea2b74e95cb9c99e747b/amqp-5.3.1-py3-none-any.whl", hash = "sha256:43b3319e1b4e7d1251833a93d672b4af1e40f3d632d479b98661a95f117880a2", size = 50944, upload-time = "2024-11-12T19:55:41.782Z" },
]

[[package]]
name = "asgiref"
version = "3.11.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/76/b9/4db2509eabd14b4a8c71d1b24c8d5734c52b8560a7b1e1a8b56c8d25568b/asgiref-3.11.0.tar.gz", hash = "sha256:13acff32519542a1736223fb79a715acdebe24286d98e8b164a73085f40da2c4", size = 37969, upload-time = "2025-11-19T15:32:20.106Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/91/be/317c2c55b8bbec407257d45f5c8d1b6867abc76d12043f2d3d58c538a4ea/asgiref-3.11.0-py3-none-any.whl", hash = "sha256:1db9021efadb0d9512ce8ffaf72fcef601c7b73a8807a1bb2ef143dc6b14846d", size = 24096, upload-time = "2025-11-19T15:32:19.004Z" },
]

[[package]]
name = "attrs"
version = "25.4.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/6b/5c/685e6633917e101e5dcb62b9dd76946cbb57c26e133bae9e0cd36033c0a9/attrs-25.4.0.tar.gz", hash = "sha256:16d5969b87f0859ef33a48b35d55ac1be6e42ae49d5e853b597db70c35c57e11", size = 934251, upload-time = "2025-10-06T13:54:44.725Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/3a/2a/7cc015f5b9f5db42b7d48157e23356022889fc354a2813c15934b7cb5c0e/attrs-25.4.0-py3-none-any.whl", hash = "sha256:adcf7e2a1fb3b36ac48d97835bb6d8ade15b8dcce26aba8bf1d14847b57a3373", size = 67615, upload-time = "2025-10-06T13:54:43.17Z" },
]

[[package]]
name = "billiard"
version = "4.2.4"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/58/23/b12ac0bcdfb7360d664f40a00b1bda139cbbbced012c34e375506dbd0143/billiard-4.2.4.tar.gz", hash = "sha256:55f542c371209e03cd5862299b74e52e4fbcba8250ba611ad94276b369b6a85f", size = 156537, upload-time = "2025-11-30T13:28:48.52Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/cb/87/8bab77b323f16d67be364031220069f79159117dd5e43eeb4be2fef1ac9b/billiard-4.2.4-py3-none-any.whl", hash = "sha256:525b42bdec68d2b983347ac312f892db930858495db601b5836ac24e6477cde5", size = 87070, upload-time = "2025-11-30T13:28:47.016Z" },
]

[[package]]
name = "black"
version = "25.12.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "click" },
    { name = "mypy-extensions" },
    { name = "packaging" },
    { name = "pathspec" },
    { name = "platformdirs" },
    { name = "pytokens" },
]
sdist = { url = "https://files.pythonhosted.org/packages/c4/d9/07b458a3f1c525ac392b5edc6b191ff140b596f9d77092429417a54e249d/black-25.12.0.tar.gz", hash = "sha256:8d3dd9cea14bff7ddc0eb243c811cdb1a011ebb4800a5f0335a01a68654796a7", size = 659264, upload-time = "2025-12-08T01:40:52.501Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/d1/bd/26083f805115db17fda9877b3c7321d08c647df39d0df4c4ca8f8450593e/black-25.12.0-cp312-cp312-macosx_10_13_x86_64.whl", hash = "sha256:31f96b7c98c1ddaeb07dc0f56c652e25bdedaac76d5b68a059d998b57c55594a", size = 1924178, upload-time = "2025-12-08T01:49:51.048Z" },
    { url = "https://files.pythonhosted.org/packages/89/6b/ea00d6651561e2bdd9231c4177f4f2ae19cc13a0b0574f47602a7519b6ca/black-25.12.0-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:05dd459a19e218078a1f98178c13f861fe6a9a5f88fc969ca4d9b49eb1809783", size = 1742643, upload-time = "2025-12-08T01:49:59.09Z" },
    { url = "https://files.pythonhosted.org/packages/6d/f3/360fa4182e36e9875fabcf3a9717db9d27a8d11870f21cff97725c54f35b/black-25.12.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:c1f68c5eff61f226934be6b5b80296cf6939e5d2f0c2f7d543ea08b204bfaf59", size = 1800158, upload-time = "2025-12-08T01:44:27.301Z" },
    { url = "https://files.pythonhosted.org/packages/f8/08/2c64830cb6616278067e040acca21d4f79727b23077633953081c9445d61/black-25.12.0-cp312-cp312-win_amd64.whl", hash = "sha256:274f940c147ddab4442d316b27f9e332ca586d39c85ecf59ebdea82cc9ee8892", size = 1426197, upload-time = "2025-12-08T01:45:51.198Z" },
    { url = "https://files.pythonhosted.org/packages/d4/60/a93f55fd9b9816b7432cf6842f0e3000fdd5b7869492a04b9011a133ee37/black-25.12.0-cp312-cp312-win_arm64.whl", hash = "sha256:169506ba91ef21e2e0591563deda7f00030cb466e747c4b09cb0a9dae5db2f43", size = 1237266, upload-time = "2025-12-08T01:45:10.556Z" },
    { url = "https://files.pythonhosted.org/packages/c8/52/c551e36bc95495d2aa1a37d50566267aa47608c81a53f91daa809e03293f/black-25.12.0-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:a05ddeb656534c3e27a05a29196c962877c83fa5503db89e68857d1161ad08a5", size = 1923809, upload-time = "2025-12-08T01:46:55.126Z" },
    { url = "https://files.pythonhosted.org/packages/a0/f7/aac9b014140ee56d247e707af8db0aae2e9efc28d4a8aba92d0abd7ae9d1/black-25.12.0-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:9ec77439ef3e34896995503865a85732c94396edcc739f302c5673a2315e1e7f", size = 1742384, upload-time = "2025-12-08T01:49:37.022Z" },
    { url = "https://files.pythonhosted.org/packages/74/98/38aaa018b2ab06a863974c12b14a6266badc192b20603a81b738c47e902e/black-25.12.0-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:0e509c858adf63aa61d908061b52e580c40eae0dfa72415fa47ac01b12e29baf", size = 1798761, upload-time = "2025-12-08T01:46:05.386Z" },
    { url = "https://files.pythonhosted.org/packages/16/3a/a8ac542125f61574a3f015b521ca83b47321ed19bb63fe6d7560f348bfe1/black-25.12.0-cp313-cp313-win_amd64.whl", hash = "sha256:252678f07f5bac4ff0d0e9b261fbb029fa530cfa206d0a636a34ab445ef8ca9d", size = 1429180, upload-time = "2025-12-08T01:45:34.903Z" },
    { url = "https://files.pythonhosted.org/packages/e6/2d/bdc466a3db9145e946762d52cd55b1385509d9f9004fec1c97bdc8debbfb/black-25.12.0-cp313-cp313-win_arm64.whl", hash = "sha256:bc5b1c09fe3c931ddd20ee548511c64ebf964ada7e6f0763d443947fd1c603ce", size = 1239350, upload-time = "2025-12-08T01:46:09.458Z" },
    { url = "https://files.pythonhosted.org/packages/35/46/1d8f2542210c502e2ae1060b2e09e47af6a5e5963cb78e22ec1a11170b28/black-25.12.0-cp314-cp314-macosx_10_15_x86_64.whl", hash = "sha256:0a0953b134f9335c2434864a643c842c44fba562155c738a2a37a4d61f00cad5", size = 1917015, upload-time = "2025-12-08T01:53:27.987Z" },
    { url = "https://files.pythonhosted.org/packages/41/37/68accadf977672beb8e2c64e080f568c74159c1aaa6414b4cd2aef2d7906/black-25.12.0-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:2355bbb6c3b76062870942d8cc450d4f8ac71f9c93c40122762c8784df49543f", size = 1741830, upload-time = "2025-12-08T01:54:36.861Z" },
    { url = "https://files.pythonhosted.org/packages/ac/76/03608a9d8f0faad47a3af3a3c8c53af3367f6c0dd2d23a84710456c7ac56/black-25.12.0-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:9678bd991cc793e81d19aeeae57966ee02909877cb65838ccffef24c3ebac08f", size = 1791450, upload-time = "2025-12-08T01:44:52.581Z" },
    { url = "https://files.pythonhosted.org/packages/06/99/b2a4bd7dfaea7964974f947e1c76d6886d65fe5d24f687df2d85406b2609/black-25.12.0-cp314-cp314-win_amd64.whl", hash = "sha256:97596189949a8aad13ad12fcbb4ae89330039b96ad6742e6f6b45e75ad5cfd83", size = 1452042, upload-time = "2025-12-08T01:46:13.188Z" },
    { url = "https://files.pythonhosted.org/packages/b2/7c/d9825de75ae5dd7795d007681b752275ea85a1c5d83269b4b9c754c2aaab/black-25.12.0-cp314-cp314-win_arm64.whl", hash = "sha256:778285d9ea197f34704e3791ea9404cd6d07595745907dd2ce3da7a13627b29b", size = 1267446, upload-time = "2025-12-08T01:46:14.497Z" },
    { url = "https://files.pythonhosted.org/packages/68/11/21331aed19145a952ad28fca2756a1433ee9308079bd03bd898e903a2e53/black-25.12.0-py3-none-any.whl", hash = "sha256:48ceb36c16dbc84062740049eef990bb2ce07598272e673c17d1a7720c71c828", size = 206191, upload-time = "2025-12-08T01:40:50.963Z" },
]

[[package]]
name = "brotli"
version = "1.2.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/f7/16/c92ca344d646e71a43b8bb353f0a6490d7f6e06210f8554c8f874e454285/brotli-1.2.0.tar.gz", hash = "sha256:e310f77e41941c13340a95976fe66a8a95b01e783d430eeaf7a2f87e0a57dd0a", size = 7388632, upload-time = "2025-11-05T18:39:42.86Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/11/ee/b0a11ab2315c69bb9b45a2aaed022499c9c24a205c3a49c3513b541a7967/brotli-1.2.0-cp312-cp312-macosx_10_13_universal2.whl", hash = "sha256:35d382625778834a7f3061b15423919aa03e4f5da34ac8e02c074e4b75ab4f84", size = 861543, upload-time = "2025-11-05T18:38:24.183Z" },
    { url = "https://files.pythonhosted.org/packages/e1/2f/29c1459513cd35828e25531ebfcbf3e92a5e49f560b1777a9af7203eb46e/brotli-1.2.0-cp312-cp312-macosx_10_13_x86_64.whl", hash = "sha256:7a61c06b334bd99bc5ae84f1eeb36bfe01400264b3c352f968c6e30a10f9d08b", size = 444288, upload-time = "2025-11-05T18:38:25.139Z" },
    { url = "https://files.pythonhosted.org/packages/3d/6f/feba03130d5fceadfa3a1bb102cb14650798c848b1df2a808356f939bb16/brotli-1.2.0-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:acec55bb7c90f1dfc476126f9711a8e81c9af7fb617409a9ee2953115343f08d", size = 1528071, upload-time = "2025-11-05T18:38:26.081Z" },
    { url = "https://files.pythonhosted.org/packages/2b/38/f3abb554eee089bd15471057ba85f47e53a44a462cfce265d9bf7088eb09/brotli-1.2.0-cp312-cp312-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:260d3692396e1895c5034f204f0db022c056f9e2ac841593a4cf9426e2a3faca", size = 1626913, upload-time = "2025-11-05T18:38:27.284Z" },
    { url = "https://files.pythonhosted.org/packages/03/a7/03aa61fbc3c5cbf99b44d158665f9b0dd3d8059be16c460208d9e385c837/brotli-1.2.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:072e7624b1fc4d601036ab3f4f27942ef772887e876beff0301d261210bca97f", size = 1419762, upload-time = "2025-11-05T18:38:28.295Z" },
    { url = "https://files.pythonhosted.org/packages/21/1b/0374a89ee27d152a5069c356c96b93afd1b94eae83f1e004b57eb6ce2f10/brotli-1.2.0-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:adedc4a67e15327dfdd04884873c6d5a01d3e3b6f61406f99b1ed4865a2f6d28", size = 1484494, upload-time = "2025-11-05T18:38:29.29Z" },
    { url = "https://files.pythonhosted.org/packages/cf/57/69d4fe84a67aef4f524dcd075c6eee868d7850e85bf01d778a857d8dbe0a/brotli-1.2.0-cp312-cp312-musllinux_1_2_ppc64le.whl", hash = "sha256:7a47ce5c2288702e09dc22a44d0ee6152f2c7eda97b3c8482d826a1f3cfc7da7", size = 1593302, upload-time = "2025-11-05T18:38:30.639Z" },
    { url = "https://files.pythonhosted.org/packages/d5/3b/39e13ce78a8e9a621c5df3aeb5fd181fcc8caba8c48a194cd629771f6828/brotli-1.2.0-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:af43b8711a8264bb4e7d6d9a6d004c3a2019c04c01127a868709ec29962b6036", size = 1487913, upload-time = "2025-11-05T18:38:31.618Z" },
    { url = "https://files.pythonhosted.org/packages/62/28/4d00cb9bd76a6357a66fcd54b4b6d70288385584063f4b07884c1e7286ac/brotli-1.2.0-cp312-cp312-win32.whl", hash = "sha256:e99befa0b48f3cd293dafeacdd0d191804d105d279e0b387a32054c1180f3161", size = 334362, upload-time = "2025-11-05T18:38:32.939Z" },
    { url = "https://files.pythonhosted.org/packages/1c/4e/bc1dcac9498859d5e353c9b153627a3752868a9d5f05ce8dedd81a2354ab/brotli-1.2.0-cp312-cp312-win_amd64.whl", hash = "sha256:b35c13ce241abdd44cb8ca70683f20c0c079728a36a996297adb5334adfc1c44", size = 369115, upload-time = "2025-11-05T18:38:33.765Z" },
    { url = "https://files.pythonhosted.org/packages/6c/d4/4ad5432ac98c73096159d9ce7ffeb82d151c2ac84adcc6168e476bb54674/brotli-1.2.0-cp313-cp313-macosx_10_13_universal2.whl", hash = "sha256:9e5825ba2c9998375530504578fd4d5d1059d09621a02065d1b6bfc41a8e05ab", size = 861523, upload-time = "2025-11-05T18:38:34.67Z" },
    { url = "https://files.pythonhosted.org/packages/91/9f/9cc5bd03ee68a85dc4bc89114f7067c056a3c14b3d95f171918c088bf88d/brotli-1.2.0-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:0cf8c3b8ba93d496b2fae778039e2f5ecc7cff99df84df337ca31d8f2252896c", size = 444289, upload-time = "2025-11-05T18:38:35.6Z" },
    { url = "https://files.pythonhosted.org/packages/2e/b6/fe84227c56a865d16a6614e2c4722864b380cb14b13f3e6bef441e73a85a/brotli-1.2.0-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:c8565e3cdc1808b1a34714b553b262c5de5fbda202285782173ec137fd13709f", size = 1528076, upload-time = "2025-11-05T18:38:36.639Z" },
    { url = "https://files.pythonhosted.org/packages/55/de/de4ae0aaca06c790371cf6e7ee93a024f6b4bb0568727da8c3de112e726c/brotli-1.2.0-cp313-cp313-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:26e8d3ecb0ee458a9804f47f21b74845cc823fd1bb19f02272be70774f56e2a6", size = 1626880, upload-time = "2025-11-05T18:38:37.623Z" },
    { url = "https://files.pythonhosted.org/packages/5f/16/a1b22cbea436642e071adcaf8d4b350a2ad02f5e0ad0da879a1be16188a0/brotli-1.2.0-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:67a91c5187e1eec76a61625c77a6c8c785650f5b576ca732bd33ef58b0dff49c", size = 1419737, upload-time = "2025-11-05T18:38:38.729Z" },
    { url = "https://files.pythonhosted.org/packages/46/63/c968a97cbb3bdbf7f974ef5a6ab467a2879b82afbc5ffb65b8acbb744f95/brotli-1.2.0-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:4ecdb3b6dc36e6d6e14d3a1bdc6c1057c8cbf80db04031d566eb6080ce283a48", size = 1484440, upload-time = "2025-11-05T18:38:39.916Z" },
    { url = "https://files.pythonhosted.org/packages/06/9d/102c67ea5c9fc171f423e8399e585dabea29b5bc79b05572891e70013cdd/brotli-1.2.0-cp313-cp313-musllinux_1_2_ppc64le.whl", hash = "sha256:3e1b35d56856f3ed326b140d3c6d9db91740f22e14b06e840fe4bb1923439a18", size = 1593313, upload-time = "2025-11-05T18:38:41.24Z" },
    { url = "https://files.pythonhosted.org/packages/9e/4a/9526d14fa6b87bc827ba1755a8440e214ff90de03095cacd78a64abe2b7d/brotli-1.2.0-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:54a50a9dad16b32136b2241ddea9e4df159b41247b2ce6aac0b3276a66a8f1e5", size = 1487945, upload-time = "2025-11-05T18:38:42.277Z" },
    { url = "https://files.pythonhosted.org/packages/5b/e8/3fe1ffed70cbef83c5236166acaed7bb9c766509b157854c80e2f766b38c/brotli-1.2.0-cp313-cp313-win32.whl", hash = "sha256:1b1d6a4efedd53671c793be6dd760fcf2107da3a52331ad9ea429edf0902f27a", size = 334368, upload-time = "2025-11-05T18:38:43.345Z" },
    { url = "https://files.pythonhosted.org/packages/ff/91/e739587be970a113b37b821eae8097aac5a48e5f0eca438c22e4c7dd8648/brotli-1.2.0-cp313-cp313-win_amd64.whl", hash = "sha256:b63daa43d82f0cdabf98dee215b375b4058cce72871fd07934f179885aad16e8", size = 369116, upload-time = "2025-11-05T18:38:44.609Z" },
    { url = "https://files.pythonhosted.org/packages/17/e1/298c2ddf786bb7347a1cd71d63a347a79e5712a7c0cba9e3c3458ebd976f/brotli-1.2.0-cp314-cp314-macosx_10_15_universal2.whl", hash = "sha256:6c12dad5cd04530323e723787ff762bac749a7b256a5bece32b2243dd5c27b21", size = 863080, upload-time = "2025-11-05T18:38:45.503Z" },
    { url = "https://files.pythonhosted.org/packages/84/0c/aac98e286ba66868b2b3b50338ffbd85a35c7122e9531a73a37a29763d38/brotli-1.2.0-cp314-cp314-macosx_10_15_x86_64.whl", hash = "sha256:3219bd9e69868e57183316ee19c84e03e8f8b5a1d1f2667e1aa8c2f91cb061ac", size = 445453, upload-time = "2025-11-05T18:38:46.433Z" },
    { url = "https://files.pythonhosted.org/packages/ec/f1/0ca1f3f99ae300372635ab3fe2f7a79fa335fee3d874fa7f9e68575e0e62/brotli-1.2.0-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:963a08f3bebd8b75ac57661045402da15991468a621f014be54e50f53a58d19e", size = 1528168, upload-time = "2025-11-05T18:38:47.371Z" },
    { url = "https://files.pythonhosted.org/packages/d6/a6/2ebfc8f766d46df8d3e65b880a2e220732395e6d7dc312c1e1244b0f074a/brotli-1.2.0-cp314-cp314-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:9322b9f8656782414b37e6af884146869d46ab85158201d82bab9abbcb971dc7", size = 1627098, upload-time = "2025-11-05T18:38:48.385Z" },
    { url = "https://files.pythonhosted.org/packages/f3/2f/0976d5b097ff8a22163b10617f76b2557f15f0f39d6a0fe1f02b1a53e92b/brotli-1.2.0-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:cf9cba6f5b78a2071ec6fb1e7bd39acf35071d90a81231d67e92d637776a6a63", size = 1419861, upload-time = "2025-11-05T18:38:49.372Z" },
    { url = "https://files.pythonhosted.org/packages/9c/97/d76df7176a2ce7616ff94c1fb72d307c9a30d2189fe877f3dd99af00ea5a/brotli-1.2.0-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:7547369c4392b47d30a3467fe8c3330b4f2e0f7730e45e3103d7d636678a808b", size = 1484594, upload-time = "2025-11-05T18:38:50.655Z" },
    { url = "https://files.pythonhosted.org/packages/d3/93/14cf0b1216f43df5609f5b272050b0abd219e0b54ea80b47cef9867b45e7/brotli-1.2.0-cp314-cp314-musllinux_1_2_ppc64le.whl", hash = "sha256:fc1530af5c3c275b8524f2e24841cbe2599d74462455e9bae5109e9ff42e9361", size = 1593455, upload-time = "2025-11-05T18:38:51.624Z" },
    { url = "https://files.pythonhosted.org/packages/b3/73/3183c9e41ca755713bdf2cc1d0810df742c09484e2e1ddd693bee53877c1/brotli-1.2.0-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:d2d085ded05278d1c7f65560aae97b3160aeb2ea2c0b3e26204856beccb60888", size = 1488164, upload-time = "2025-11-05T18:38:53.079Z" },
    { url = "https://files.pythonhosted.org/packages/64/6a/0c78d8f3a582859236482fd9fa86a65a60328a00983006bcf6d83b7b2253/brotli-1.2.0-cp314-cp314-win32.whl", hash = "sha256:832c115a020e463c2f67664560449a7bea26b0c1fdd690352addad6d0a08714d", size = 339280, upload-time = "2025-11-05T18:38:54.02Z" },
    { url = "https://files.pythonhosted.org/packages/f5/10/56978295c14794b2c12007b07f3e41ba26acda9257457d7085b0bb3bb90c/brotli-1.2.0-cp314-cp314-win_amd64.whl", hash = "sha256:e7c0af964e0b4e3412a0ebf341ea26ec767fa0b4cf81abb5e897c9338b5ad6a3", size = 375639, upload-time = "2025-11-05T18:38:55.67Z" },
]

[[package]]
name = "brotlicffi"
version = "1.2.0.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "cffi" },
]
sdist = { url = "https://files.pythonhosted.org/packages/84/85/57c314a6b35336efbbdc13e5fc9ae13f6b60a0647cfa7c1221178ac6d8ae/brotlicffi-1.2.0.0.tar.gz", hash = "sha256:34345d8d1f9d534fcac2249e57a4c3c8801a33c9942ff9f8574f67a175e17adb", size = 476682, upload-time = "2025-11-21T18:17:57.334Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/e4/df/a72b284d8c7bef0ed5756b41c2eb7d0219a1dd6ac6762f1c7bdbc31ef3af/brotlicffi-1.2.0.0-cp38-abi3-macosx_11_0_arm64.whl", hash = "sha256:9458d08a7ccde8e3c0afedbf2c70a8263227a68dea5ab13590593f4c0a4fd5f4", size = 432340, upload-time = "2025-11-21T18:17:42.277Z" },
    { url = "https://files.pythonhosted.org/packages/74/2b/cc55a2d1d6fb4f5d458fba44a3d3f91fb4320aa14145799fd3a996af0686/brotlicffi-1.2.0.0-cp38-abi3-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:84e3d0020cf1bd8b8131f4a07819edee9f283721566fe044a20ec792ca8fd8b7", size = 1534002, upload-time = "2025-11-21T18:17:43.746Z" },
    { url = "https://files.pythonhosted.org/packages/e4/9c/d51486bf366fc7d6735f0e46b5b96ca58dc005b250263525a1eea3cd5d21/brotlicffi-1.2.0.0-cp38-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:33cfb408d0cff64cd50bef268c0fed397c46fbb53944aa37264148614a62e990", size = 1536547, upload-time = "2025-11-21T18:17:45.729Z" },
    { url = "https://files.pythonhosted.org/packages/1b/37/293a9a0a7caf17e6e657668bebb92dfe730305999fe8c0e2703b8888789c/brotlicffi-1.2.0.0-cp38-abi3-win32.whl", hash = "sha256:23e5c912fdc6fd37143203820230374d24babd078fc054e18070a647118158f6", size = 343085, upload-time = "2025-11-21T18:17:48.887Z" },
    { url = "https://files.pythonhosted.org/packages/07/6b/6e92009df3b8b7272f85a0992b306b61c34b7ea1c4776643746e61c380ac/brotlicffi-1.2.0.0-cp38-abi3-win_amd64.whl", hash = "sha256:f139a7cdfe4ae7859513067b736eb44d19fae1186f9e99370092f6915216451b", size = 378586, upload-time = "2025-11-21T18:17:50.531Z" },
]

[[package]]
name = "celery"
version = "5.6.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "billiard" },
    { name = "click" },
    { name = "click-didyoumean" },
    { name = "click-plugins" },
    { name = "click-repl" },
    { name = "exceptiongroup" },
    { name = "kombu" },
    { name = "python-dateutil" },
    { name = "tzlocal" },
    { name = "vine" },
]
sdist = { url = "https://files.pythonhosted.org/packages/ad/5f/b681ae3c89290d2ea6562ea96b40f5af6f6fc5f7743e2cd1a19e47721548/celery-5.6.0.tar.gz", hash = "sha256:641405206042d52ae460e4e9751a2e31b06cf80ab836fcf92e0b9311d7ea8113", size = 1712522, upload-time = "2025-11-30T17:39:46.282Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/01/4e/53a125038d6a814491a0ae3457435c13cf8821eb602292cf9db37ce35f62/celery-5.6.0-py3-none-any.whl", hash = "sha256:33cf01477b175017fc8f22c5ee8a65157591043ba8ca78a443fe703aa910f581", size = 444561, upload-time = "2025-11-30T17:39:44.314Z" },
]

[[package]]
name = "certifi"
version = "2025.11.12"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/a2/8c/58f469717fa48465e4a50c014a0400602d3c437d7c0c468e17ada824da3a/certifi-2025.11.12.tar.gz", hash = "sha256:d8ab5478f2ecd78af242878415affce761ca6bc54a22a27e026d7c25357c3316", size = 160538, upload-time = "2025-11-12T02:54:51.517Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/70/7d/9bc192684cea499815ff478dfcdc13835ddf401365057044fb721ec6bddb/certifi-2025.11.12-py3-none-any.whl", hash = "sha256:97de8790030bbd5c2d96b7ec782fc2f7820ef8dba6db909ccf95449f2d062d4b", size = 159438, upload-time = "2025-11-12T02:54:49.735Z" },
]

[[package]]
name = "cffi"
version = "2.0.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "pycparser", marker = "implementation_name != 'PyPy'" },
]
sdist = { url = "https://files.pythonhosted.org/packages/eb/56/b1ba7935a17738ae8453301356628e8147c79dbb825bcbc73dc7401f9846/cffi-2.0.0.tar.gz", hash = "sha256:44d1b5909021139fe36001ae048dbdde8214afa20200eda0f64c068cac5d5529", size = 523588, upload-time = "2025-09-08T23:24:04.541Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/ea/47/4f61023ea636104d4f16ab488e268b93008c3d0bb76893b1b31db1f96802/cffi-2.0.0-cp312-cp312-macosx_10_13_x86_64.whl", hash = "sha256:6d02d6655b0e54f54c4ef0b94eb6be0607b70853c45ce98bd278dc7de718be5d", size = 185271, upload-time = "2025-09-08T23:22:44.795Z" },
    { url = "https://files.pythonhosted.org/packages/df/a2/781b623f57358e360d62cdd7a8c681f074a71d445418a776eef0aadb4ab4/cffi-2.0.0-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:8eca2a813c1cb7ad4fb74d368c2ffbbb4789d377ee5bb8df98373c2cc0dee76c", size = 181048, upload-time = "2025-09-08T23:22:45.938Z" },
    { url = "https://files.pythonhosted.org/packages/ff/df/a4f0fbd47331ceeba3d37c2e51e9dfc9722498becbeec2bd8bc856c9538a/cffi-2.0.0-cp312-cp312-manylinux1_i686.manylinux2014_i686.manylinux_2_17_i686.manylinux_2_5_i686.whl", hash = "sha256:21d1152871b019407d8ac3985f6775c079416c282e431a4da6afe7aefd2bccbe", size = 212529, upload-time = "2025-09-08T23:22:47.349Z" },
    { url = "https://files.pythonhosted.org/packages/d5/72/12b5f8d3865bf0f87cf1404d8c374e7487dcf097a1c91c436e72e6badd83/cffi-2.0.0-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:b21e08af67b8a103c71a250401c78d5e0893beff75e28c53c98f4de42f774062", size = 220097, upload-time = "2025-09-08T23:22:48.677Z" },
    { url = "https://files.pythonhosted.org/packages/c2/95/7a135d52a50dfa7c882ab0ac17e8dc11cec9d55d2c18dda414c051c5e69e/cffi-2.0.0-cp312-cp312-manylinux2014_ppc64le.manylinux_2_17_ppc64le.whl", hash = "sha256:1e3a615586f05fc4065a8b22b8152f0c1b00cdbc60596d187c2a74f9e3036e4e", size = 207983, upload-time = "2025-09-08T23:22:50.06Z" },
    { url = "https://files.pythonhosted.org/packages/3a/c8/15cb9ada8895957ea171c62dc78ff3e99159ee7adb13c0123c001a2546c1/cffi-2.0.0-cp312-cp312-manylinux2014_s390x.manylinux_2_17_s390x.whl", hash = "sha256:81afed14892743bbe14dacb9e36d9e0e504cd204e0b165062c488942b9718037", size = 206519, upload-time = "2025-09-08T23:22:51.364Z" },
    { url = "https://files.pythonhosted.org/packages/78/2d/7fa73dfa841b5ac06c7b8855cfc18622132e365f5b81d02230333ff26e9e/cffi-2.0.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:3e17ed538242334bf70832644a32a7aae3d83b57567f9fd60a26257e992b79ba", size = 219572, upload-time = "2025-09-08T23:22:52.902Z" },
    { url = "https://files.pythonhosted.org/packages/07/e0/267e57e387b4ca276b90f0434ff88b2c2241ad72b16d31836adddfd6031b/cffi-2.0.0-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:3925dd22fa2b7699ed2617149842d2e6adde22b262fcbfada50e3d195e4b3a94", size = 222963, upload-time = "2025-09-08T23:22:54.518Z" },
    { url = "https://files.pythonhosted.org/packages/b6/75/1f2747525e06f53efbd878f4d03bac5b859cbc11c633d0fb81432d98a795/cffi-2.0.0-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:2c8f814d84194c9ea681642fd164267891702542f028a15fc97d4674b6206187", size = 221361, upload-time = "2025-09-08T23:22:55.867Z" },
    { url = "https://files.pythonhosted.org/packages/7b/2b/2b6435f76bfeb6bbf055596976da087377ede68df465419d192acf00c437/cffi-2.0.0-cp312-cp312-win32.whl", hash = "sha256:da902562c3e9c550df360bfa53c035b2f241fed6d9aef119048073680ace4a18", size = 172932, upload-time = "2025-09-08T23:22:57.188Z" },
    { url = "https://files.pythonhosted.org/packages/f8/ed/13bd4418627013bec4ed6e54283b1959cf6db888048c7cf4b4c3b5b36002/cffi-2.0.0-cp312-cp312-win_amd64.whl", hash = "sha256:da68248800ad6320861f129cd9c1bf96ca849a2771a59e0344e88681905916f5", size = 183557, upload-time = "2025-09-08T23:22:58.351Z" },
    { url = "https://files.pythonhosted.org/packages/95/31/9f7f93ad2f8eff1dbc1c3656d7ca5bfd8fb52c9d786b4dcf19b2d02217fa/cffi-2.0.0-cp312-cp312-win_arm64.whl", hash = "sha256:4671d9dd5ec934cb9a73e7ee9676f9362aba54f7f34910956b84d727b0d73fb6", size = 177762, upload-time = "2025-09-08T23:22:59.668Z" },
    { url = "https://files.pythonhosted.org/packages/4b/8d/a0a47a0c9e413a658623d014e91e74a50cdd2c423f7ccfd44086ef767f90/cffi-2.0.0-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:00bdf7acc5f795150faa6957054fbbca2439db2f775ce831222b66f192f03beb", size = 185230, upload-time = "2025-09-08T23:23:00.879Z" },
    { url = "https://files.pythonhosted.org/packages/4a/d2/a6c0296814556c68ee32009d9c2ad4f85f2707cdecfd7727951ec228005d/cffi-2.0.0-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:45d5e886156860dc35862657e1494b9bae8dfa63bf56796f2fb56e1679fc0bca", size = 181043, upload-time = "2025-09-08T23:23:02.231Z" },
    { url = "https://files.pythonhosted.org/packages/b0/1e/d22cc63332bd59b06481ceaac49d6c507598642e2230f201649058a7e704/cffi-2.0.0-cp313-cp313-manylinux1_i686.manylinux2014_i686.manylinux_2_17_i686.manylinux_2_5_i686.whl", hash = "sha256:07b271772c100085dd28b74fa0cd81c8fb1a3ba18b21e03d7c27f3436a10606b", size = 212446, upload-time = "2025-09-08T23:23:03.472Z" },
    { url = "https://files.pythonhosted.org/packages/a9/f5/a2c23eb03b61a0b8747f211eb716446c826ad66818ddc7810cc2cc19b3f2/cffi-2.0.0-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:d48a880098c96020b02d5a1f7d9251308510ce8858940e6fa99ece33f610838b", size = 220101, upload-time = "2025-09-08T23:23:04.792Z" },
    { url = "https://files.pythonhosted.org/packages/f2/7f/e6647792fc5850d634695bc0e6ab4111ae88e89981d35ac269956605feba/cffi-2.0.0-cp313-cp313-manylinux2014_ppc64le.manylinux_2_17_ppc64le.whl", hash = "sha256:f93fd8e5c8c0a4aa1f424d6173f14a892044054871c771f8566e4008eaa359d2", size = 207948, upload-time = "2025-09-08T23:23:06.127Z" },
    { url = "https://files.pythonhosted.org/packages/cb/1e/a5a1bd6f1fb30f22573f76533de12a00bf274abcdc55c8edab639078abb6/cffi-2.0.0-cp313-cp313-manylinux2014_s390x.manylinux_2_17_s390x.whl", hash = "sha256:dd4f05f54a52fb558f1ba9f528228066954fee3ebe629fc1660d874d040ae5a3", size = 206422, upload-time = "2025-09-08T23:23:07.753Z" },
    { url = "https://files.pythonhosted.org/packages/98/df/0a1755e750013a2081e863e7cd37e0cdd02664372c754e5560099eb7aa44/cffi-2.0.0-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:c8d3b5532fc71b7a77c09192b4a5a200ea992702734a2e9279a37f2478236f26", size = 219499, upload-time = "2025-09-08T23:23:09.648Z" },
    { url = "https://files.pythonhosted.org/packages/50/e1/a969e687fcf9ea58e6e2a928ad5e2dd88cc12f6f0ab477e9971f2309b57c/cffi-2.0.0-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:d9b29c1f0ae438d5ee9acb31cadee00a58c46cc9c0b2f9038c6b0b3470877a8c", size = 222928, upload-time = "2025-09-08T23:23:10.928Z" },
    { url = "https://files.pythonhosted.org/packages/36/54/0362578dd2c9e557a28ac77698ed67323ed5b9775ca9d3fe73fe191bb5d8/cffi-2.0.0-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:6d50360be4546678fc1b79ffe7a66265e28667840010348dd69a314145807a1b", size = 221302, upload-time = "2025-09-08T23:23:12.42Z" },
    { url = "https://files.pythonhosted.org/packages/eb/6d/bf9bda840d5f1dfdbf0feca87fbdb64a918a69bca42cfa0ba7b137c48cb8/cffi-2.0.0-cp313-cp313-win32.whl", hash = "sha256:74a03b9698e198d47562765773b4a8309919089150a0bb17d829ad7b44b60d27", size = 172909, upload-time = "2025-09-08T23:23:14.32Z" },
    { url = "https://files.pythonhosted.org/packages/37/18/6519e1ee6f5a1e579e04b9ddb6f1676c17368a7aba48299c3759bbc3c8b3/cffi-2.0.0-cp313-cp313-win_amd64.whl", hash = "sha256:19f705ada2530c1167abacb171925dd886168931e0a7b78f5bffcae5c6b5be75", size = 183402, upload-time = "2025-09-08T23:23:15.535Z" },
    { url = "https://files.pythonhosted.org/packages/cb/0e/02ceeec9a7d6ee63bb596121c2c8e9b3a9e150936f4fbef6ca1943e6137c/cffi-2.0.0-cp313-cp313-win_arm64.whl", hash = "sha256:256f80b80ca3853f90c21b23ee78cd008713787b1b1e93eae9f3d6a7134abd91", size = 177780, upload-time = "2025-09-08T23:23:16.761Z" },
    { url = "https://files.pythonhosted.org/packages/92/c4/3ce07396253a83250ee98564f8d7e9789fab8e58858f35d07a9a2c78de9f/cffi-2.0.0-cp314-cp314-macosx_10_13_x86_64.whl", hash = "sha256:fc33c5141b55ed366cfaad382df24fe7dcbc686de5be719b207bb248e3053dc5", size = 185320, upload-time = "2025-09-08T23:23:18.087Z" },
    { url = "https://files.pythonhosted.org/packages/59/dd/27e9fa567a23931c838c6b02d0764611c62290062a6d4e8ff7863daf9730/cffi-2.0.0-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:c654de545946e0db659b3400168c9ad31b5d29593291482c43e3564effbcee13", size = 181487, upload-time = "2025-09-08T23:23:19.622Z" },
    { url = "https://files.pythonhosted.org/packages/d6/43/0e822876f87ea8a4ef95442c3d766a06a51fc5298823f884ef87aaad168c/cffi-2.0.0-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:24b6f81f1983e6df8db3adc38562c83f7d4a0c36162885ec7f7b77c7dcbec97b", size = 220049, upload-time = "2025-09-08T23:23:20.853Z" },
    { url = "https://files.pythonhosted.org/packages/b4/89/76799151d9c2d2d1ead63c2429da9ea9d7aac304603de0c6e8764e6e8e70/cffi-2.0.0-cp314-cp314-manylinux2014_ppc64le.manylinux_2_17_ppc64le.whl", hash = "sha256:12873ca6cb9b0f0d3a0da705d6086fe911591737a59f28b7936bdfed27c0d47c", size = 207793, upload-time = "2025-09-08T23:23:22.08Z" },
    { url = "https://files.pythonhosted.org/packages/bb/dd/3465b14bb9e24ee24cb88c9e3730f6de63111fffe513492bf8c808a3547e/cffi-2.0.0-cp314-cp314-manylinux2014_s390x.manylinux_2_17_s390x.whl", hash = "sha256:d9b97165e8aed9272a6bb17c01e3cc5871a594a446ebedc996e2397a1c1ea8ef", size = 206300, upload-time = "2025-09-08T23:23:23.314Z" },
    { url = "https://files.pythonhosted.org/packages/47/d9/d83e293854571c877a92da46fdec39158f8d7e68da75bf73581225d28e90/cffi-2.0.0-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:afb8db5439b81cf9c9d0c80404b60c3cc9c3add93e114dcae767f1477cb53775", size = 219244, upload-time = "2025-09-08T23:23:24.541Z" },
    { url = "https://files.pythonhosted.org/packages/2b/0f/1f177e3683aead2bb00f7679a16451d302c436b5cbf2505f0ea8146ef59e/cffi-2.0.0-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:737fe7d37e1a1bffe70bd5754ea763a62a066dc5913ca57e957824b72a85e205", size = 222828, upload-time = "2025-09-08T23:23:26.143Z" },
    { url = "https://files.pythonhosted.org/packages/c6/0f/cafacebd4b040e3119dcb32fed8bdef8dfe94da653155f9d0b9dc660166e/cffi-2.0.0-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:38100abb9d1b1435bc4cc340bb4489635dc2f0da7456590877030c9b3d40b0c1", size = 220926, upload-time = "2025-09-08T23:23:27.873Z" },
    { url = "https://files.pythonhosted.org/packages/3e/aa/df335faa45b395396fcbc03de2dfcab242cd61a9900e914fe682a59170b1/cffi-2.0.0-cp314-cp314-win32.whl", hash = "sha256:087067fa8953339c723661eda6b54bc98c5625757ea62e95eb4898ad5e776e9f", size = 175328, upload-time = "2025-09-08T23:23:44.61Z" },
    { url = "https://files.pythonhosted.org/packages/bb/92/882c2d30831744296ce713f0feb4c1cd30f346ef747b530b5318715cc367/cffi-2.0.0-cp314-cp314-win_amd64.whl", hash = "sha256:203a48d1fb583fc7d78a4c6655692963b860a417c0528492a6bc21f1aaefab25", size = 185650, upload-time = "2025-09-08T23:23:45.848Z" },
    { url = "https://files.pythonhosted.org/packages/9f/2c/98ece204b9d35a7366b5b2c6539c350313ca13932143e79dc133ba757104/cffi-2.0.0-cp314-cp314-win_arm64.whl", hash = "sha256:dbd5c7a25a7cb98f5ca55d258b103a2054f859a46ae11aaf23134f9cc0d356ad", size = 180687, upload-time = "2025-09-08T23:23:47.105Z" },
    { url = "https://files.pythonhosted.org/packages/3e/61/c768e4d548bfa607abcda77423448df8c471f25dbe64fb2ef6d555eae006/cffi-2.0.0-cp314-cp314t-macosx_10_13_x86_64.whl", hash = "sha256:9a67fc9e8eb39039280526379fb3a70023d77caec1852002b4da7e8b270c4dd9", size = 188773, upload-time = "2025-09-08T23:23:29.347Z" },
    { url = "https://files.pythonhosted.org/packages/2c/ea/5f76bce7cf6fcd0ab1a1058b5af899bfbef198bea4d5686da88471ea0336/cffi-2.0.0-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:7a66c7204d8869299919db4d5069a82f1561581af12b11b3c9f48c584eb8743d", size = 185013, upload-time = "2025-09-08T23:23:30.63Z" },
    { url = "https://files.pythonhosted.org/packages/be/b4/c56878d0d1755cf9caa54ba71e5d049479c52f9e4afc230f06822162ab2f/cffi-2.0.0-cp314-cp314t-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:7cc09976e8b56f8cebd752f7113ad07752461f48a58cbba644139015ac24954c", size = 221593, upload-time = "2025-09-08T23:23:31.91Z" },
    { url = "https://files.pythonhosted.org/packages/e0/0d/eb704606dfe8033e7128df5e90fee946bbcb64a04fcdaa97321309004000/cffi-2.0.0-cp314-cp314t-manylinux2014_ppc64le.manylinux_2_17_ppc64le.whl", hash = "sha256:92b68146a71df78564e4ef48af17551a5ddd142e5190cdf2c5624d0c3ff5b2e8", size = 209354, upload-time = "2025-09-08T23:23:33.214Z" },
    { url = "https://files.pythonhosted.org/packages/d8/19/3c435d727b368ca475fb8742ab97c9cb13a0de600ce86f62eab7fa3eea60/cffi-2.0.0-cp314-cp314t-manylinux2014_s390x.manylinux_2_17_s390x.whl", hash = "sha256:b1e74d11748e7e98e2f426ab176d4ed720a64412b6a15054378afdb71e0f37dc", size = 208480, upload-time = "2025-09-08T23:23:34.495Z" },
    { url = "https://files.pythonhosted.org/packages/d0/44/681604464ed9541673e486521497406fadcc15b5217c3e326b061696899a/cffi-2.0.0-cp314-cp314t-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:28a3a209b96630bca57cce802da70c266eb08c6e97e5afd61a75611ee6c64592", size = 221584, upload-time = "2025-09-08T23:23:36.096Z" },
    { url = "https://files.pythonhosted.org/packages/25/8e/342a504ff018a2825d395d44d63a767dd8ebc927ebda557fecdaca3ac33a/cffi-2.0.0-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:7553fb2090d71822f02c629afe6042c299edf91ba1bf94951165613553984512", size = 224443, upload-time = "2025-09-08T23:23:37.328Z" },
    { url = "https://files.pythonhosted.org/packages/e1/5e/b666bacbbc60fbf415ba9988324a132c9a7a0448a9a8f125074671c0f2c3/cffi-2.0.0-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:6c6c373cfc5c83a975506110d17457138c8c63016b563cc9ed6e056a82f13ce4", size = 223437, upload-time = "2025-09-08T23:23:38.945Z" },
    { url = "https://files.pythonhosted.org/packages/a0/1d/ec1a60bd1a10daa292d3cd6bb0b359a81607154fb8165f3ec95fe003b85c/cffi-2.0.0-cp314-cp314t-win32.whl", hash = "sha256:1fc9ea04857caf665289b7a75923f2c6ed559b8298a1b8c49e59f7dd95c8481e", size = 180487, upload-time = "2025-09-08T23:23:40.423Z" },
    { url = "https://files.pythonhosted.org/packages/bf/41/4c1168c74fac325c0c8156f04b6749c8b6a8f405bbf91413ba088359f60d/cffi-2.0.0-cp314-cp314t-win_amd64.whl", hash = "sha256:d68b6cef7827e8641e8ef16f4494edda8b36104d79773a334beaa1e3521430f6", size = 191726, upload-time = "2025-09-08T23:23:41.742Z" },
    { url = "https://files.pythonhosted.org/packages/ae/3a/dbeec9d1ee0844c679f6bb5d6ad4e9f198b1224f4e7a32825f47f6192b0c/cffi-2.0.0-cp314-cp314t-win_arm64.whl", hash = "sha256:0a1527a803f0a659de1af2e1fd700213caba79377e27e4693648c2923da066f9", size = 184195, upload-time = "2025-09-08T23:23:43.004Z" },
]

[[package]]
name = "charset-normalizer"
version = "3.4.4"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/13/69/33ddede1939fdd074bce5434295f38fae7136463422fe4fd3e0e89b98062/charset_normalizer-3.4.4.tar.gz", hash = "sha256:94537985111c35f28720e43603b8e7b43a6ecfb2ce1d3058bbe955b73404e21a", size = 129418, upload-time = "2025-10-14T04:42:32.879Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/f3/85/1637cd4af66fa687396e757dec650f28025f2a2f5a5531a3208dc0ec43f2/charset_normalizer-3.4.4-cp312-cp312-macosx_10_13_universal2.whl", hash = "sha256:0a98e6759f854bd25a58a73fa88833fba3b7c491169f86ce1180c948ab3fd394", size = 208425, upload-time = "2025-10-14T04:40:53.353Z" },
    { url = "https://files.pythonhosted.org/packages/9d/6a/04130023fef2a0d9c62d0bae2649b69f7b7d8d24ea5536feef50551029df/charset_normalizer-3.4.4-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:b5b290ccc2a263e8d185130284f8501e3e36c5e02750fc6b6bdeb2e9e96f1e25", size = 148162, upload-time = "2025-10-14T04:40:54.558Z" },
    { url = "https://files.pythonhosted.org/packages/78/29/62328d79aa60da22c9e0b9a66539feae06ca0f5a4171ac4f7dc285b83688/charset_normalizer-3.4.4-cp312-cp312-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:74bb723680f9f7a6234dcf67aea57e708ec1fbdf5699fb91dfd6f511b0a320ef", size = 144558, upload-time = "2025-10-14T04:40:55.677Z" },
    { url = "https://files.pythonhosted.org/packages/86/bb/b32194a4bf15b88403537c2e120b817c61cd4ecffa9b6876e941c3ee38fe/charset_normalizer-3.4.4-cp312-cp312-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:f1e34719c6ed0b92f418c7c780480b26b5d9c50349e9a9af7d76bf757530350d", size = 161497, upload-time = "2025-10-14T04:40:57.217Z" },
    { url = "https://files.pythonhosted.org/packages/19/89/a54c82b253d5b9b111dc74aca196ba5ccfcca8242d0fb64146d4d3183ff1/charset_normalizer-3.4.4-cp312-cp312-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:2437418e20515acec67d86e12bf70056a33abdacb5cb1655042f6538d6b085a8", size = 159240, upload-time = "2025-10-14T04:40:58.358Z" },
    { url = "https://files.pythonhosted.org/packages/c0/10/d20b513afe03acc89ec33948320a5544d31f21b05368436d580dec4e234d/charset_normalizer-3.4.4-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:11d694519d7f29d6cd09f6ac70028dba10f92f6cdd059096db198c283794ac86", size = 153471, upload-time = "2025-10-14T04:40:59.468Z" },
    { url = "https://files.pythonhosted.org/packages/61/fa/fbf177b55bdd727010f9c0a3c49eefa1d10f960e5f09d1d887bf93c2e698/charset_normalizer-3.4.4-cp312-cp312-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:ac1c4a689edcc530fc9d9aa11f5774b9e2f33f9a0c6a57864e90908f5208d30a", size = 150864, upload-time = "2025-10-14T04:41:00.623Z" },
    { url = "https://files.pythonhosted.org/packages/05/12/9fbc6a4d39c0198adeebbde20b619790e9236557ca59fc40e0e3cebe6f40/charset_normalizer-3.4.4-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:21d142cc6c0ec30d2efee5068ca36c128a30b0f2c53c1c07bd78cb6bc1d3be5f", size = 150647, upload-time = "2025-10-14T04:41:01.754Z" },
    { url = "https://files.pythonhosted.org/packages/ad/1f/6a9a593d52e3e8c5d2b167daf8c6b968808efb57ef4c210acb907c365bc4/charset_normalizer-3.4.4-cp312-cp312-musllinux_1_2_armv7l.whl", hash = "sha256:5dbe56a36425d26d6cfb40ce79c314a2e4dd6211d51d6d2191c00bed34f354cc", size = 145110, upload-time = "2025-10-14T04:41:03.231Z" },
    { url = "https://files.pythonhosted.org/packages/30/42/9a52c609e72471b0fc54386dc63c3781a387bb4fe61c20231a4ebcd58bdd/charset_normalizer-3.4.4-cp312-cp312-musllinux_1_2_ppc64le.whl", hash = "sha256:5bfbb1b9acf3334612667b61bd3002196fe2a1eb4dd74d247e0f2a4d50ec9bbf", size = 162839, upload-time = "2025-10-14T04:41:04.715Z" },
    { url = "https://files.pythonhosted.org/packages/c4/5b/c0682bbf9f11597073052628ddd38344a3d673fda35a36773f7d19344b23/charset_normalizer-3.4.4-cp312-cp312-musllinux_1_2_riscv64.whl", hash = "sha256:d055ec1e26e441f6187acf818b73564e6e6282709e9bcb5b63f5b23068356a15", size = 150667, upload-time = "2025-10-14T04:41:05.827Z" },
    { url = "https://files.pythonhosted.org/packages/e4/24/a41afeab6f990cf2daf6cb8c67419b63b48cf518e4f56022230840c9bfb2/charset_normalizer-3.4.4-cp312-cp312-musllinux_1_2_s390x.whl", hash = "sha256:af2d8c67d8e573d6de5bc30cdb27e9b95e49115cd9baad5ddbd1a6207aaa82a9", size = 160535, upload-time = "2025-10-14T04:41:06.938Z" },
    { url = "https://files.pythonhosted.org/packages/2a/e5/6a4ce77ed243c4a50a1fecca6aaaab419628c818a49434be428fe24c9957/charset_normalizer-3.4.4-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:780236ac706e66881f3b7f2f32dfe90507a09e67d1d454c762cf642e6e1586e0", size = 154816, upload-time = "2025-10-14T04:41:08.101Z" },
    { url = "https://files.pythonhosted.org/packages/a8/ef/89297262b8092b312d29cdb2517cb1237e51db8ecef2e9af5edbe7b683b1/charset_normalizer-3.4.4-cp312-cp312-win32.whl", hash = "sha256:5833d2c39d8896e4e19b689ffc198f08ea58116bee26dea51e362ecc7cd3ed26", size = 99694, upload-time = "2025-10-14T04:41:09.23Z" },
    { url = "https://files.pythonhosted.org/packages/3d/2d/1e5ed9dd3b3803994c155cd9aacb60c82c331bad84daf75bcb9c91b3295e/charset_normalizer-3.4.4-cp312-cp312-win_amd64.whl", hash = "sha256:a79cfe37875f822425b89a82333404539ae63dbdddf97f84dcbc3d339aae9525", size = 107131, upload-time = "2025-10-14T04:41:10.467Z" },
    { url = "https://files.pythonhosted.org/packages/d0/d9/0ed4c7098a861482a7b6a95603edce4c0d9db2311af23da1fb2b75ec26fc/charset_normalizer-3.4.4-cp312-cp312-win_arm64.whl", hash = "sha256:376bec83a63b8021bb5c8ea75e21c4ccb86e7e45ca4eb81146091b56599b80c3", size = 100390, upload-time = "2025-10-14T04:41:11.915Z" },
    { url = "https://files.pythonhosted.org/packages/97/45/4b3a1239bbacd321068ea6e7ac28875b03ab8bc0aa0966452db17cd36714/charset_normalizer-3.4.4-cp313-cp313-macosx_10_13_universal2.whl", hash = "sha256:e1f185f86a6f3403aa2420e815904c67b2f9ebc443f045edd0de921108345794", size = 208091, upload-time = "2025-10-14T04:41:13.346Z" },
    { url = "https://files.pythonhosted.org/packages/7d/62/73a6d7450829655a35bb88a88fca7d736f9882a27eacdca2c6d505b57e2e/charset_normalizer-3.4.4-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:6b39f987ae8ccdf0d2642338faf2abb1862340facc796048b604ef14919e55ed", size = 147936, upload-time = "2025-10-14T04:41:14.461Z" },
    { url = "https://files.pythonhosted.org/packages/89/c5/adb8c8b3d6625bef6d88b251bbb0d95f8205831b987631ab0c8bb5d937c2/charset_normalizer-3.4.4-cp313-cp313-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:3162d5d8ce1bb98dd51af660f2121c55d0fa541b46dff7bb9b9f86ea1d87de72", size = 144180, upload-time = "2025-10-14T04:41:15.588Z" },
    { url = "https://files.pythonhosted.org/packages/91/ed/9706e4070682d1cc219050b6048bfd293ccf67b3d4f5a4f39207453d4b99/charset_normalizer-3.4.4-cp313-cp313-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:81d5eb2a312700f4ecaa977a8235b634ce853200e828fbadf3a9c50bab278328", size = 161346, upload-time = "2025-10-14T04:41:16.738Z" },
    { url = "https://files.pythonhosted.org/packages/d5/0d/031f0d95e4972901a2f6f09ef055751805ff541511dc1252ba3ca1f80cf5/charset_normalizer-3.4.4-cp313-cp313-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:5bd2293095d766545ec1a8f612559f6b40abc0eb18bb2f5d1171872d34036ede", size = 158874, upload-time = "2025-10-14T04:41:17.923Z" },
    { url = "https://files.pythonhosted.org/packages/f5/83/6ab5883f57c9c801ce5e5677242328aa45592be8a00644310a008d04f922/charset_normalizer-3.4.4-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:a8a8b89589086a25749f471e6a900d3f662d1d3b6e2e59dcecf787b1cc3a1894", size = 153076, upload-time = "2025-10-14T04:41:19.106Z" },
    { url = "https://files.pythonhosted.org/packages/75/1e/5ff781ddf5260e387d6419959ee89ef13878229732732ee73cdae01800f2/charset_normalizer-3.4.4-cp313-cp313-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:bc7637e2f80d8530ee4a78e878bce464f70087ce73cf7c1caf142416923b98f1", size = 150601, upload-time = "2025-10-14T04:41:20.245Z" },
    { url = "https://files.pythonhosted.org/packages/d7/57/71be810965493d3510a6ca79b90c19e48696fb1ff964da319334b12677f0/charset_normalizer-3.4.4-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:f8bf04158c6b607d747e93949aa60618b61312fe647a6369f88ce2ff16043490", size = 150376, upload-time = "2025-10-14T04:41:21.398Z" },
    { url = "https://files.pythonhosted.org/packages/e5/d5/c3d057a78c181d007014feb7e9f2e65905a6c4ef182c0ddf0de2924edd65/charset_normalizer-3.4.4-cp313-cp313-musllinux_1_2_armv7l.whl", hash = "sha256:554af85e960429cf30784dd47447d5125aaa3b99a6f0683589dbd27e2f45da44", size = 144825, upload-time = "2025-10-14T04:41:22.583Z" },
    { url = "https://files.pythonhosted.org/packages/e6/8c/d0406294828d4976f275ffbe66f00266c4b3136b7506941d87c00cab5272/charset_normalizer-3.4.4-cp313-cp313-musllinux_1_2_ppc64le.whl", hash = "sha256:74018750915ee7ad843a774364e13a3db91682f26142baddf775342c3f5b1133", size = 162583, upload-time = "2025-10-14T04:41:23.754Z" },
    { url = "https://files.pythonhosted.org/packages/d7/24/e2aa1f18c8f15c4c0e932d9287b8609dd30ad56dbe41d926bd846e22fb8d/charset_normalizer-3.4.4-cp313-cp313-musllinux_1_2_riscv64.whl", hash = "sha256:c0463276121fdee9c49b98908b3a89c39be45d86d1dbaa22957e38f6321d4ce3", size = 150366, upload-time = "2025-10-14T04:41:25.27Z" },
    { url = "https://files.pythonhosted.org/packages/e4/5b/1e6160c7739aad1e2df054300cc618b06bf784a7a164b0f238360721ab86/charset_normalizer-3.4.4-cp313-cp313-musllinux_1_2_s390x.whl", hash = "sha256:362d61fd13843997c1c446760ef36f240cf81d3ebf74ac62652aebaf7838561e", size = 160300, upload-time = "2025-10-14T04:41:26.725Z" },
    { url = "https://files.pythonhosted.org/packages/7a/10/f882167cd207fbdd743e55534d5d9620e095089d176d55cb22d5322f2afd/charset_normalizer-3.4.4-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:9a26f18905b8dd5d685d6d07b0cdf98a79f3c7a918906af7cc143ea2e164c8bc", size = 154465, upload-time = "2025-10-14T04:41:28.322Z" },
    { url = "https://files.pythonhosted.org/packages/89/66/c7a9e1b7429be72123441bfdbaf2bc13faab3f90b933f664db506dea5915/charset_normalizer-3.4.4-cp313-cp313-win32.whl", hash = "sha256:9b35f4c90079ff2e2edc5b26c0c77925e5d2d255c42c74fdb70fb49b172726ac", size = 99404, upload-time = "2025-10-14T04:41:29.95Z" },
    { url = "https://files.pythonhosted.org/packages/c4/26/b9924fa27db384bdcd97ab83b4f0a8058d96ad9626ead570674d5e737d90/charset_normalizer-3.4.4-cp313-cp313-win_amd64.whl", hash = "sha256:b435cba5f4f750aa6c0a0d92c541fb79f69a387c91e61f1795227e4ed9cece14", size = 107092, upload-time = "2025-10-14T04:41:31.188Z" },
    { url = "https://files.pythonhosted.org/packages/af/8f/3ed4bfa0c0c72a7ca17f0380cd9e4dd842b09f664e780c13cff1dcf2ef1b/charset_normalizer-3.4.4-cp313-cp313-win_arm64.whl", hash = "sha256:542d2cee80be6f80247095cc36c418f7bddd14f4a6de45af91dfad36d817bba2", size = 100408, upload-time = "2025-10-14T04:41:32.624Z" },
    { url = "https://files.pythonhosted.org/packages/2a/35/7051599bd493e62411d6ede36fd5af83a38f37c4767b92884df7301db25d/charset_normalizer-3.4.4-cp314-cp314-macosx_10_13_universal2.whl", hash = "sha256:da3326d9e65ef63a817ecbcc0df6e94463713b754fe293eaa03da99befb9a5bd", size = 207746, upload-time = "2025-10-14T04:41:33.773Z" },
    { url = "https://files.pythonhosted.org/packages/10/9a/97c8d48ef10d6cd4fcead2415523221624bf58bcf68a802721a6bc807c8f/charset_normalizer-3.4.4-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:8af65f14dc14a79b924524b1e7fffe304517b2bff5a58bf64f30b98bbc5079eb", size = 147889, upload-time = "2025-10-14T04:41:34.897Z" },
    { url = "https://files.pythonhosted.org/packages/10/bf/979224a919a1b606c82bd2c5fa49b5c6d5727aa47b4312bb27b1734f53cd/charset_normalizer-3.4.4-cp314-cp314-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:74664978bb272435107de04e36db5a9735e78232b85b77d45cfb38f758efd33e", size = 143641, upload-time = "2025-10-14T04:41:36.116Z" },
    { url = "https://files.pythonhosted.org/packages/ba/33/0ad65587441fc730dc7bd90e9716b30b4702dc7b617e6ba4997dc8651495/charset_normalizer-3.4.4-cp314-cp314-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:752944c7ffbfdd10c074dc58ec2d5a8a4cd9493b314d367c14d24c17684ddd14", size = 160779, upload-time = "2025-10-14T04:41:37.229Z" },
    { url = "https://files.pythonhosted.org/packages/67/ed/331d6b249259ee71ddea93f6f2f0a56cfebd46938bde6fcc6f7b9a3d0e09/charset_normalizer-3.4.4-cp314-cp314-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:d1f13550535ad8cff21b8d757a3257963e951d96e20ec82ab44bc64aeb62a191", size = 159035, upload-time = "2025-10-14T04:41:38.368Z" },
    { url = "https://files.pythonhosted.org/packages/67/ff/f6b948ca32e4f2a4576aa129d8bed61f2e0543bf9f5f2b7fc3758ed005c9/charset_normalizer-3.4.4-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:ecaae4149d99b1c9e7b88bb03e3221956f68fd6d50be2ef061b2381b61d20838", size = 152542, upload-time = "2025-10-14T04:41:39.862Z" },
    { url = "https://files.pythonhosted.org/packages/16/85/276033dcbcc369eb176594de22728541a925b2632f9716428c851b149e83/charset_normalizer-3.4.4-cp314-cp314-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:cb6254dc36b47a990e59e1068afacdcd02958bdcce30bb50cc1700a8b9d624a6", size = 149524, upload-time = "2025-10-14T04:41:41.319Z" },
    { url = "https://files.pythonhosted.org/packages/9e/f2/6a2a1f722b6aba37050e626530a46a68f74e63683947a8acff92569f979a/charset_normalizer-3.4.4-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:c8ae8a0f02f57a6e61203a31428fa1d677cbe50c93622b4149d5c0f319c1d19e", size = 150395, upload-time = "2025-10-14T04:41:42.539Z" },
    { url = "https://files.pythonhosted.org/packages/60/bb/2186cb2f2bbaea6338cad15ce23a67f9b0672929744381e28b0592676824/charset_normalizer-3.4.4-cp314-cp314-musllinux_1_2_armv7l.whl", hash = "sha256:47cc91b2f4dd2833fddaedd2893006b0106129d4b94fdb6af1f4ce5a9965577c", size = 143680, upload-time = "2025-10-14T04:41:43.661Z" },
    { url = "https://files.pythonhosted.org/packages/7d/a5/bf6f13b772fbb2a90360eb620d52ed8f796f3c5caee8398c3b2eb7b1c60d/charset_normalizer-3.4.4-cp314-cp314-musllinux_1_2_ppc64le.whl", hash = "sha256:82004af6c302b5d3ab2cfc4cc5f29db16123b1a8417f2e25f9066f91d4411090", size = 162045, upload-time = "2025-10-14T04:41:44.821Z" },
    { url = "https://files.pythonhosted.org/packages/df/c5/d1be898bf0dc3ef9030c3825e5d3b83f2c528d207d246cbabe245966808d/charset_normalizer-3.4.4-cp314-cp314-musllinux_1_2_riscv64.whl", hash = "sha256:2b7d8f6c26245217bd2ad053761201e9f9680f8ce52f0fcd8d0755aeae5b2152", size = 149687, upload-time = "2025-10-14T04:41:46.442Z" },
    { url = "https://files.pythonhosted.org/packages/a5/42/90c1f7b9341eef50c8a1cb3f098ac43b0508413f33affd762855f67a410e/charset_normalizer-3.4.4-cp314-cp314-musllinux_1_2_s390x.whl", hash = "sha256:799a7a5e4fb2d5898c60b640fd4981d6a25f1c11790935a44ce38c54e985f828", size = 160014, upload-time = "2025-10-14T04:41:47.631Z" },
    { url = "https://files.pythonhosted.org/packages/76/be/4d3ee471e8145d12795ab655ece37baed0929462a86e72372fd25859047c/charset_normalizer-3.4.4-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:99ae2cffebb06e6c22bdc25801d7b30f503cc87dbd283479e7b606f70aff57ec", size = 154044, upload-time = "2025-10-14T04:41:48.81Z" },
    { url = "https://files.pythonhosted.org/packages/b0/6f/8f7af07237c34a1defe7defc565a9bc1807762f672c0fde711a4b22bf9c0/charset_normalizer-3.4.4-cp314-cp314-win32.whl", hash = "sha256:f9d332f8c2a2fcbffe1378594431458ddbef721c1769d78e2cbc06280d8155f9", size = 99940, upload-time = "2025-10-14T04:41:49.946Z" },
    { url = "https://files.pythonhosted.org/packages/4b/51/8ade005e5ca5b0d80fb4aff72a3775b325bdc3d27408c8113811a7cbe640/charset_normalizer-3.4.4-cp314-cp314-win_amd64.whl", hash = "sha256:8a6562c3700cce886c5be75ade4a5db4214fda19fede41d9792d100288d8f94c", size = 107104, upload-time = "2025-10-14T04:41:51.051Z" },
    { url = "https://files.pythonhosted.org/packages/da/5f/6b8f83a55bb8278772c5ae54a577f3099025f9ade59d0136ac24a0df4bde/charset_normalizer-3.4.4-cp314-cp314-win_arm64.whl", hash = "sha256:de00632ca48df9daf77a2c65a484531649261ec9f25489917f09e455cb09ddb2", size = 100743, upload-time = "2025-10-14T04:41:52.122Z" },
    { url = "https://files.pythonhosted.org/packages/0a/4c/925909008ed5a988ccbb72dcc897407e5d6d3bd72410d69e051fc0c14647/charset_normalizer-3.4.4-py3-none-any.whl", hash = "sha256:7a32c560861a02ff789ad905a2fe94e3f840803362c84fecf1851cb4cf3dc37f", size = 53402, upload-time = "2025-10-14T04:42:31.76Z" },
]

[[package]]
name = "click"
version = "8.3.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "colorama", marker = "sys_platform == 'win32'" },
]
sdist = { url = "https://files.pythonhosted.org/packages/3d/fa/656b739db8587d7b5dfa22e22ed02566950fbfbcdc20311993483657a5c0/click-8.3.1.tar.gz", hash = "sha256:12ff4785d337a1bb490bb7e9c2b1ee5da3112e94a8622f26a6c77f5d2fc6842a", size = 295065, upload-time = "2025-11-15T20:45:42.706Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/98/78/01c019cdb5d6498122777c1a43056ebb3ebfeef2076d9d026bfe15583b2b/click-8.3.1-py3-none-any.whl", hash = "sha256:981153a64e25f12d547d3426c367a4857371575ee7ad18df2a6183ab0545b2a6", size = 108274, upload-time = "2025-11-15T20:45:41.139Z" },
]

[[package]]
name = "click-didyoumean"
version = "0.3.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "click" },
]
sdist = { url = "https://files.pythonhosted.org/packages/30/ce/217289b77c590ea1e7c24242d9ddd6e249e52c795ff10fac2c50062c48cb/click_didyoumean-0.3.1.tar.gz", hash = "sha256:4f82fdff0dbe64ef8ab2279bd6aa3f6a99c3b28c05aa09cbfc07c9d7fbb5a463", size = 3089, upload-time = "2024-03-24T08:22:07.499Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/1b/5b/974430b5ffdb7a4f1941d13d83c64a0395114503cc357c6b9ae4ce5047ed/click_didyoumean-0.3.1-py3-none-any.whl", hash = "sha256:5c4bb6007cfea5f2fd6583a2fb6701a22a41eb98957e63d0fac41c10e7c3117c", size = 3631, upload-time = "2024-03-24T08:22:06.356Z" },
]

[[package]]
name = "click-plugins"
version = "1.1.1.2"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "click" },
]
sdist = { url = "https://files.pythonhosted.org/packages/c3/a4/34847b59150da33690a36da3681d6bbc2ec14ee9a846bc30a6746e5984e4/click_plugins-1.1.1.2.tar.gz", hash = "sha256:d7af3984a99d243c131aa1a828331e7630f4a88a9741fd05c927b204bcf92261", size = 8343, upload-time = "2025-06-25T00:47:37.555Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/3d/9a/2abecb28ae875e39c8cad711eb1186d8d14eab564705325e77e4e6ab9ae5/click_plugins-1.1.1.2-py2.py3-none-any.whl", hash = "sha256:008d65743833ffc1f5417bf0e78e8d2c23aab04d9745ba817bd3e71b0feb6aa6", size = 11051, upload-time = "2025-06-25T00:47:36.731Z" },
]

[[package]]
name = "click-repl"
version = "0.3.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "click" },
    { name = "prompt-toolkit" },
]
sdist = { url = "https://files.pythonhosted.org/packages/cb/a2/57f4ac79838cfae6912f997b4d1a64a858fb0c86d7fcaae6f7b58d267fca/click-repl-0.3.0.tar.gz", hash = "sha256:17849c23dba3d667247dc4defe1757fff98694e90fe37474f3feebb69ced26a9", size = 10449, upload-time = "2023-06-15T12:43:51.141Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/52/40/9d857001228658f0d59e97ebd4c346fe73e138c6de1bce61dc568a57c7f8/click_repl-0.3.0-py3-none-any.whl", hash = "sha256:fb7e06deb8da8de86180a33a9da97ac316751c094c6899382da7feeeeb51b812", size = 10289, upload-time = "2023-06-15T12:43:48.626Z" },
]

[[package]]
name = "colorama"
version = "0.4.6"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/d8/53/6f443c9a4a8358a93a6792e2acffb9d9d5cb0a5cfd8802644b7b1c9a02e4/colorama-0.4.6.tar.gz", hash = "sha256:08695f5cb7ed6e0531a20572697297273c47b8cae5a63ffc6d6ed5c201be6e44", size = 27697, upload-time = "2022-10-25T02:36:22.414Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/d1/d6/3965ed04c63042e047cb6a3e6ed1a63a35087b6a609aa3a15ed8ac56c221/colorama-0.4.6-py2.py3-none-any.whl", hash = "sha256:4f1d9991f5acc0ca119f9d443620b77f9d6b33703e51011c16baf57afb285fc6", size = 25335, upload-time = "2022-10-25T02:36:20.889Z" },
]

[[package]]
name = "cssselect2"
version = "0.8.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "tinycss2" },
    { name = "webencodings" },
]
sdist = { url = "https://files.pythonhosted.org/packages/9f/86/fd7f58fc498b3166f3a7e8e0cddb6e620fe1da35b02248b1bd59e95dbaaa/cssselect2-0.8.0.tar.gz", hash = "sha256:7674ffb954a3b46162392aee2a3a0aedb2e14ecf99fcc28644900f4e6e3e9d3a", size = 35716, upload-time = "2025-03-05T14:46:07.988Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/0f/e7/aa315e6a749d9b96c2504a1ba0ba031ba2d0517e972ce22682e3fccecb09/cssselect2-0.8.0-py3-none-any.whl", hash = "sha256:46fc70ebc41ced7a32cd42d58b1884d72ade23d21e5a4eaaf022401c13f0e76e", size = 15454, upload-time = "2025-03-05T14:46:06.463Z" },
]

[[package]]
name = "django"
version = "6.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "asgiref" },
    { name = "sqlparse" },
    { name = "tzdata", marker = "sys_platform == 'win32'" },
]
sdist = { url = "https://files.pythonhosted.org/packages/15/75/19762bfc4ea556c303d9af8e36f0cd910ab17dff6c8774644314427a2120/django-6.0.tar.gz", hash = "sha256:7b0c1f50c0759bbe6331c6a39c89ae022a84672674aeda908784617ef47d8e26", size = 10932418, upload-time = "2025-12-03T16:26:21.878Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/d7/ae/f19e24789a5ad852670d6885f5480f5e5895576945fcc01817dfd9bc002a/django-6.0-py3-none-any.whl", hash = "sha256:1cc2c7344303bbfb7ba5070487c17f7fc0b7174bbb0a38cebf03c675f5f19b6d", size = 8339181, upload-time = "2025-12-03T16:26:16.231Z" },
]

[[package]]
name = "django-allauth"
version = "65.13.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "asgiref" },
    { name = "django" },
]
sdist = { url = "https://files.pythonhosted.org/packages/e0/b7/42a048ba1dedbb6b553f5376a6126b1c753c10c70d1edab8f94c560c8066/django_allauth-65.13.1.tar.gz", hash = "sha256:2af0d07812f8c1a8e3732feaabe6a9db5ecf3fad6b45b6a0f7fd825f656c5a15", size = 1983857, upload-time = "2025-11-20T16:34:40.811Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/d8/98/9d44ae1468abfdb521d651fb67f914165c7812dfdd97be16190c9b1cc246/django_allauth-65.13.1-py3-none-any.whl", hash = "sha256:2887294beedfd108b4b52ebd182e0ed373deaeb927fc5a22f77bbde3174704a6", size = 1787349, upload-time = "2025-11-20T16:34:37.354Z" },
]

[[package]]
name = "django-cors-headers"
version = "4.9.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "asgiref" },
    { name = "django" },
]
sdist = { url = "https://files.pythonhosted.org/packages/21/39/55822b15b7ec87410f34cd16ce04065ff390e50f9e29f31d6d116fc80456/django_cors_headers-4.9.0.tar.gz", hash = "sha256:fe5d7cb59fdc2c8c646ce84b727ac2bca8912a247e6e68e1fb507372178e59e8", size = 21458, upload-time = "2025-09-18T10:40:52.326Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/30/d8/19ed1e47badf477d17fb177c1c19b5a21da0fd2d9f093f23be3fb86c5fab/django_cors_headers-4.9.0-py3-none-any.whl", hash = "sha256:15c7f20727f90044dcee2216a9fd7303741a864865f0c3657e28b7056f61b449", size = 12809, upload-time = "2025-09-18T10:40:50.843Z" },
]

[[package]]
name = "django-environ"
version = "0.12.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/d6/04/65d2521842c42f4716225f20d8443a50804920606aec018188bbee30a6b0/django_environ-0.12.0.tar.gz", hash = "sha256:227dc891453dd5bde769c3449cf4a74b6f2ee8f7ab2361c93a07068f4179041a", size = 56804, upload-time = "2025-01-13T17:03:37.74Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/83/b3/0a3bec4ecbfee960f39b1842c2f91e4754251e0a6ed443db9fe3f666ba8f/django_environ-0.12.0-py2.py3-none-any.whl", hash = "sha256:92fb346a158abda07ffe6eb23135ce92843af06ecf8753f43adf9d2366dcc0ca", size = 19957, upload-time = "2025-01-13T17:03:32.918Z" },
]

[[package]]
name = "djangorestframework"
version = "3.16.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "django" },
]
sdist = { url = "https://files.pythonhosted.org/packages/8a/95/5376fe618646fde6899b3cdc85fd959716bb67542e273a76a80d9f326f27/djangorestframework-3.16.1.tar.gz", hash = "sha256:166809528b1aced0a17dc66c24492af18049f2c9420dbd0be29422029cfc3ff7", size = 1089735, upload-time = "2025-08-06T17:50:53.251Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/b0/ce/bf8b9d3f415be4ac5588545b5fcdbbb841977db1c1d923f7568eeabe1689/djangorestframework-3.16.1-py3-none-any.whl", hash = "sha256:33a59f47fb9c85ede792cbf88bde71893bcda0667bc573f784649521f1102cec", size = 1080442, upload-time = "2025-08-06T17:50:50.667Z" },
]

[[package]]
name = "drf-spectacular"
version = "0.29.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "django" },
    { name = "djangorestframework" },
    { name = "inflection" },
    { name = "jsonschema" },
    { name = "pyyaml" },
    { name = "uritemplate" },
]
sdist = { url = "https://files.pythonhosted.org/packages/5e/0e/a4f50d83e76cbe797eda88fc0083c8ca970cfa362b5586359ef06ec6f70a/drf_spectacular-0.29.0.tar.gz", hash = "sha256:0a069339ea390ce7f14a75e8b5af4a0860a46e833fd4af027411a3e94fc1a0cc", size = 241722, upload-time = "2025-11-02T03:40:26.348Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/32/d9/502c56fc3ca960075d00956283f1c44e8cafe433dada03f9ed2821f3073b/drf_spectacular-0.29.0-py3-none-any.whl", hash = "sha256:d1ee7c9535d89848affb4427347f7c4a22c5d22530b8842ef133d7b72e19b41a", size = 105433, upload-time = "2025-11-02T03:40:24.823Z" },
]

[[package]]
name = "ecdsa"
version = "0.19.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "six" },
]
sdist = { url = "https://files.pythonhosted.org/packages/c0/1f/924e3caae75f471eae4b26bd13b698f6af2c44279f67af317439c2f4c46a/ecdsa-0.19.1.tar.gz", hash = "sha256:478cba7b62555866fcb3bb3fe985e06decbdb68ef55713c4e5ab98c57d508e61", size = 201793, upload-time = "2025-03-13T11:52:43.25Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/cb/a3/460c57f094a4a165c84a1341c373b0a4f5ec6ac244b998d5021aade89b77/ecdsa-0.19.1-py2.py3-none-any.whl", hash = "sha256:30638e27cf77b7e15c4c4cc1973720149e1033827cfd00661ca5c8cc0cdb24c3", size = 150607, upload-time = "2025-03-13T11:52:41.757Z" },
]

[[package]]
name = "exceptiongroup"
version = "1.3.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "typing-extensions", marker = "python_full_version < '3.13'" },
]
sdist = { url = "https://files.pythonhosted.org/packages/50/79/66800aadf48771f6b62f7eb014e352e5d06856655206165d775e675a02c9/exceptiongroup-1.3.1.tar.gz", hash = "sha256:8b412432c6055b0b7d14c310000ae93352ed6754f70fa8f7c34141f91c4e3219", size = 30371, upload-time = "2025-11-21T23:01:54.787Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/8a/0e/97c33bf5009bdbac74fd2beace167cab3f978feb69cc36f1ef79360d6c4e/exceptiongroup-1.3.1-py3-none-any.whl", hash = "sha256:a7a39a3bd276781e98394987d3a5701d0c4edffb633bb7a5144577f82c773598", size = 16740, upload-time = "2025-11-21T23:01:53.443Z" },
]

[[package]]
name = "factory-boy"
version = "3.3.3"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "faker" },
]
sdist = { url = "https://files.pythonhosted.org/packages/ba/98/75cacae9945f67cfe323829fc2ac451f64517a8a330b572a06a323997065/factory_boy-3.3.3.tar.gz", hash = "sha256:866862d226128dfac7f2b4160287e899daf54f2612778327dd03d0e2cb1e3d03", size = 164146, upload-time = "2025-02-03T09:49:04.433Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/27/8d/2bc5f5546ff2ccb3f7de06742853483ab75bf74f36a92254702f8baecc79/factory_boy-3.3.3-py2.py3-none-any.whl", hash = "sha256:1c39e3289f7e667c4285433f305f8d506efc2fe9c73aaea4151ebd5cdea394fc", size = 37036, upload-time = "2025-02-03T09:49:01.659Z" },
]

[[package]]
name = "faker"
version = "39.0.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "tzdata" },
]
sdist = { url = "https://files.pythonhosted.org/packages/30/b9/0897fb5888ddda099dc0f314a8a9afb5faa7e52eaf6865c00686dfb394db/faker-39.0.0.tar.gz", hash = "sha256:ddae46d3b27e01cea7894651d687b33bcbe19a45ef044042c721ceac6d3da0ff", size = 1941757, upload-time = "2025-12-17T19:19:04.762Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/eb/5a/26cdb1b10a55ac6eb11a738cea14865fa753606c4897d7be0f5dc230df00/faker-39.0.0-py3-none-any.whl", hash = "sha256:c72f1fca8f1a24b8da10fcaa45739135a19772218ddd61b86b7ea1b8c790dce7", size = 1980775, upload-time = "2025-12-17T19:19:02.926Z" },
]

[[package]]
name = "flake8"
version = "7.3.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "mccabe" },
    { name = "pycodestyle" },
    { name = "pyflakes" },
]
sdist = { url = "https://files.pythonhosted.org/packages/9b/af/fbfe3c4b5a657d79e5c47a2827a362f9e1b763336a52f926126aa6dc7123/flake8-7.3.0.tar.gz", hash = "sha256:fe044858146b9fc69b551a4b490d69cf960fcb78ad1edcb84e7fbb1b4a8e3872", size = 48326, upload-time = "2025-06-20T19:31:35.838Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/9f/56/13ab06b4f93ca7cac71078fbe37fcea175d3216f31f85c3168a6bbd0bb9a/flake8-7.3.0-py2.py3-none-any.whl", hash = "sha256:b9696257b9ce8beb888cdbe31cf885c90d31928fe202be0889a7cdafad32f01e", size = 57922, upload-time = "2025-06-20T19:31:34.425Z" },
]

[[package]]
name = "fonttools"
version = "4.61.1"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/ec/ca/cf17b88a8df95691275a3d77dc0a5ad9907f328ae53acbe6795da1b2f5ed/fonttools-4.61.1.tar.gz", hash = "sha256:6675329885c44657f826ef01d9e4fb33b9158e9d93c537d84ad8399539bc6f69", size = 3565756, upload-time = "2025-12-12T17:31:24.246Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/6f/16/7decaa24a1bd3a70c607b2e29f0adc6159f36a7e40eaba59846414765fd4/fonttools-4.61.1-cp312-cp312-macosx_10_13_universal2.whl", hash = "sha256:f3cb4a569029b9f291f88aafc927dd53683757e640081ca8c412781ea144565e", size = 2851593, upload-time = "2025-12-12T17:30:04.225Z" },
    { url = "https://files.pythonhosted.org/packages/94/98/3c4cb97c64713a8cf499b3245c3bf9a2b8fd16a3e375feff2aed78f96259/fonttools-4.61.1-cp312-cp312-macosx_10_13_x86_64.whl", hash = "sha256:41a7170d042e8c0024703ed13b71893519a1a6d6e18e933e3ec7507a2c26a4b2", size = 2400231, upload-time = "2025-12-12T17:30:06.47Z" },
    { url = "https://files.pythonhosted.org/packages/b7/37/82dbef0f6342eb01f54bca073ac1498433d6ce71e50c3c3282b655733b31/fonttools-4.61.1-cp312-cp312-manylinux1_x86_64.manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_5_x86_64.whl", hash = "sha256:10d88e55330e092940584774ee5e8a6971b01fc2f4d3466a1d6c158230880796", size = 4954103, upload-time = "2025-12-12T17:30:08.432Z" },
    { url = "https://files.pythonhosted.org/packages/6c/44/f3aeac0fa98e7ad527f479e161aca6c3a1e47bb6996b053d45226fe37bf2/fonttools-4.61.1-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:15acc09befd16a0fb8a8f62bc147e1a82817542d72184acca9ce6e0aeda9fa6d", size = 5004295, upload-time = "2025-12-12T17:30:10.56Z" },
    { url = "https://files.pythonhosted.org/packages/14/e8/7424ced75473983b964d09f6747fa09f054a6d656f60e9ac9324cf40c743/fonttools-4.61.1-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:e6bcdf33aec38d16508ce61fd81838f24c83c90a1d1b8c68982857038673d6b8", size = 4944109, upload-time = "2025-12-12T17:30:12.874Z" },
    { url = "https://files.pythonhosted.org/packages/c8/8b/6391b257fa3d0b553d73e778f953a2f0154292a7a7a085e2374b111e5410/fonttools-4.61.1-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:5fade934607a523614726119164ff621e8c30e8fa1ffffbbd358662056ba69f0", size = 5093598, upload-time = "2025-12-12T17:30:15.79Z" },
    { url = "https://files.pythonhosted.org/packages/d9/71/fd2ea96cdc512d92da5678a1c98c267ddd4d8c5130b76d0f7a80f9a9fde8/fonttools-4.61.1-cp312-cp312-win32.whl", hash = "sha256:75da8f28eff26defba42c52986de97b22106cb8f26515b7c22443ebc9c2d3261", size = 2269060, upload-time = "2025-12-12T17:30:18.058Z" },
    { url = "https://files.pythonhosted.org/packages/80/3b/a3e81b71aed5a688e89dfe0e2694b26b78c7d7f39a5ffd8a7d75f54a12a8/fonttools-4.61.1-cp312-cp312-win_amd64.whl", hash = "sha256:497c31ce314219888c0e2fce5ad9178ca83fe5230b01a5006726cdf3ac9f24d9", size = 2319078, upload-time = "2025-12-12T17:30:22.862Z" },
    { url = "https://files.pythonhosted.org/packages/4b/cf/00ba28b0990982530addb8dc3e9e6f2fa9cb5c20df2abdda7baa755e8fe1/fonttools-4.61.1-cp313-cp313-macosx_10_13_universal2.whl", hash = "sha256:8c56c488ab471628ff3bfa80964372fc13504ece601e0d97a78ee74126b2045c", size = 2846454, upload-time = "2025-12-12T17:30:24.938Z" },
    { url = "https://files.pythonhosted.org/packages/5a/ca/468c9a8446a2103ae645d14fee3f610567b7042aba85031c1c65e3ef7471/fonttools-4.61.1-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:dc492779501fa723b04d0ab1f5be046797fee17d27700476edc7ee9ae535a61e", size = 2398191, upload-time = "2025-12-12T17:30:27.343Z" },
    { url = "https://files.pythonhosted.org/packages/a3/4b/d67eedaed19def5967fade3297fed8161b25ba94699efc124b14fb68cdbc/fonttools-4.61.1-cp313-cp313-manylinux1_x86_64.manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_5_x86_64.whl", hash = "sha256:64102ca87e84261419c3747a0d20f396eb024bdbeb04c2bfb37e2891f5fadcb5", size = 4928410, upload-time = "2025-12-12T17:30:29.771Z" },
    { url = "https://files.pythonhosted.org/packages/b0/8d/6fb3494dfe61a46258cd93d979cf4725ded4eb46c2a4ca35e4490d84daea/fonttools-4.61.1-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:4c1b526c8d3f615a7b1867f38a9410849c8f4aef078535742198e942fba0e9bd", size = 4984460, upload-time = "2025-12-12T17:30:32.073Z" },
    { url = "https://files.pythonhosted.org/packages/f7/f1/a47f1d30b3dc00d75e7af762652d4cbc3dff5c2697a0dbd5203c81afd9c3/fonttools-4.61.1-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:41ed4b5ec103bd306bb68f81dc166e77409e5209443e5773cb4ed837bcc9b0d3", size = 4925800, upload-time = "2025-12-12T17:30:34.339Z" },
    { url = "https://files.pythonhosted.org/packages/a7/01/e6ae64a0981076e8a66906fab01539799546181e32a37a0257b77e4aa88b/fonttools-4.61.1-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:b501c862d4901792adaec7c25b1ecc749e2662543f68bb194c42ba18d6eec98d", size = 5067859, upload-time = "2025-12-12T17:30:36.593Z" },
    { url = "https://files.pythonhosted.org/packages/73/aa/28e40b8d6809a9b5075350a86779163f074d2b617c15d22343fce81918db/fonttools-4.61.1-cp313-cp313-win32.whl", hash = "sha256:4d7092bb38c53bbc78e9255a59158b150bcdc115a1e3b3ce0b5f267dc35dd63c", size = 2267821, upload-time = "2025-12-12T17:30:38.478Z" },
    { url = "https://files.pythonhosted.org/packages/1a/59/453c06d1d83dc0951b69ef692d6b9f1846680342927df54e9a1ca91c6f90/fonttools-4.61.1-cp313-cp313-win_amd64.whl", hash = "sha256:21e7c8d76f62ab13c9472ccf74515ca5b9a761d1bde3265152a6dc58700d895b", size = 2318169, upload-time = "2025-12-12T17:30:40.951Z" },
    { url = "https://files.pythonhosted.org/packages/32/8f/4e7bf82c0cbb738d3c2206c920ca34ca74ef9dabde779030145d28665104/fonttools-4.61.1-cp314-cp314-macosx_10_15_universal2.whl", hash = "sha256:fff4f534200a04b4a36e7ae3cb74493afe807b517a09e99cb4faa89a34ed6ecd", size = 2846094, upload-time = "2025-12-12T17:30:43.511Z" },
    { url = "https://files.pythonhosted.org/packages/71/09/d44e45d0a4f3a651f23a1e9d42de43bc643cce2971b19e784cc67d823676/fonttools-4.61.1-cp314-cp314-macosx_10_15_x86_64.whl", hash = "sha256:d9203500f7c63545b4ce3799319fe4d9feb1a1b89b28d3cb5abd11b9dd64147e", size = 2396589, upload-time = "2025-12-12T17:30:45.681Z" },
    { url = "https://files.pythonhosted.org/packages/89/18/58c64cafcf8eb677a99ef593121f719e6dcbdb7d1c594ae5a10d4997ca8a/fonttools-4.61.1-cp314-cp314-manylinux1_x86_64.manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_5_x86_64.whl", hash = "sha256:fa646ecec9528bef693415c79a86e733c70a4965dd938e9a226b0fc64c9d2e6c", size = 4877892, upload-time = "2025-12-12T17:30:47.709Z" },
    { url = "https://files.pythonhosted.org/packages/8a/ec/9e6b38c7ba1e09eb51db849d5450f4c05b7e78481f662c3b79dbde6f3d04/fonttools-4.61.1-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:11f35ad7805edba3aac1a3710d104592df59f4b957e30108ae0ba6c10b11dd75", size = 4972884, upload-time = "2025-12-12T17:30:49.656Z" },
    { url = "https://files.pythonhosted.org/packages/5e/87/b5339da8e0256734ba0dbbf5b6cdebb1dd79b01dc8c270989b7bcd465541/fonttools-4.61.1-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:b931ae8f62db78861b0ff1ac017851764602288575d65b8e8ff1963fed419063", size = 4924405, upload-time = "2025-12-12T17:30:51.735Z" },
    { url = "https://files.pythonhosted.org/packages/0b/47/e3409f1e1e69c073a3a6fd8cb886eb18c0bae0ee13db2c8d5e7f8495e8b7/fonttools-4.61.1-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:b148b56f5de675ee16d45e769e69f87623a4944f7443850bf9a9376e628a89d2", size = 5035553, upload-time = "2025-12-12T17:30:54.823Z" },
    { url = "https://files.pythonhosted.org/packages/bf/b6/1f6600161b1073a984294c6c031e1a56ebf95b6164249eecf30012bb2e38/fonttools-4.61.1-cp314-cp314-win32.whl", hash = "sha256:9b666a475a65f4e839d3d10473fad6d47e0a9db14a2f4a224029c5bfde58ad2c", size = 2271915, upload-time = "2025-12-12T17:30:57.913Z" },
    { url = "https://files.pythonhosted.org/packages/52/7b/91e7b01e37cc8eb0e1f770d08305b3655e4f002fc160fb82b3390eabacf5/fonttools-4.61.1-cp314-cp314-win_amd64.whl", hash = "sha256:4f5686e1fe5fce75d82d93c47a438a25bf0d1319d2843a926f741140b2b16e0c", size = 2323487, upload-time = "2025-12-12T17:30:59.804Z" },
    { url = "https://files.pythonhosted.org/packages/39/5c/908ad78e46c61c3e3ed70c3b58ff82ab48437faf84ec84f109592cabbd9f/fonttools-4.61.1-cp314-cp314t-macosx_10_15_universal2.whl", hash = "sha256:e76ce097e3c57c4bcb67c5aa24a0ecdbd9f74ea9219997a707a4061fbe2707aa", size = 2929571, upload-time = "2025-12-12T17:31:02.574Z" },
    { url = "https://files.pythonhosted.org/packages/bd/41/975804132c6dea64cdbfbaa59f3518a21c137a10cccf962805b301ac6ab2/fonttools-4.61.1-cp314-cp314t-macosx_10_15_x86_64.whl", hash = "sha256:9cfef3ab326780c04d6646f68d4b4742aae222e8b8ea1d627c74e38afcbc9d91", size = 2435317, upload-time = "2025-12-12T17:31:04.974Z" },
    { url = "https://files.pythonhosted.org/packages/b0/5a/aef2a0a8daf1ebaae4cfd83f84186d4a72ee08fd6a8451289fcd03ffa8a4/fonttools-4.61.1-cp314-cp314t-manylinux1_x86_64.manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_5_x86_64.whl", hash = "sha256:a75c301f96db737e1c5ed5fd7d77d9c34466de16095a266509e13da09751bd19", size = 4882124, upload-time = "2025-12-12T17:31:07.456Z" },
    { url = "https://files.pythonhosted.org/packages/80/33/d6db3485b645b81cea538c9d1c9219d5805f0877fda18777add4671c5240/fonttools-4.61.1-cp314-cp314t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:91669ccac46bbc1d09e9273546181919064e8df73488ea087dcac3e2968df9ba", size = 5100391, upload-time = "2025-12-12T17:31:09.732Z" },
    { url = "https://files.pythonhosted.org/packages/6c/d6/675ba631454043c75fcf76f0ca5463eac8eb0666ea1d7badae5fea001155/fonttools-4.61.1-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:c33ab3ca9d3ccd581d58e989d67554e42d8d4ded94ab3ade3508455fe70e65f7", size = 4978800, upload-time = "2025-12-12T17:31:11.681Z" },
    { url = "https://files.pythonhosted.org/packages/7f/33/d3ec753d547a8d2bdaedd390d4a814e8d5b45a093d558f025c6b990b554c/fonttools-4.61.1-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:664c5a68ec406f6b1547946683008576ef8b38275608e1cee6c061828171c118", size = 5006426, upload-time = "2025-12-12T17:31:13.764Z" },
    { url = "https://files.pythonhosted.org/packages/b4/40/cc11f378b561a67bea850ab50063366a0d1dd3f6d0a30ce0f874b0ad5664/fonttools-4.61.1-cp314-cp314t-win32.whl", hash = "sha256:aed04cabe26f30c1647ef0e8fbb207516fd40fe9472e9439695f5c6998e60ac5", size = 2335377, upload-time = "2025-12-12T17:31:16.49Z" },
    { url = "https://files.pythonhosted.org/packages/e4/ff/c9a2b66b39f8628531ea58b320d66d951267c98c6a38684daa8f50fb02f8/fonttools-4.61.1-cp314-cp314t-win_amd64.whl", hash = "sha256:2180f14c141d2f0f3da43f3a81bc8aa4684860f6b0e6f9e165a4831f24e6a23b", size = 2400613, upload-time = "2025-12-12T17:31:18.769Z" },
    { url = "https://files.pythonhosted.org/packages/c7/4e/ce75a57ff3aebf6fc1f4e9d508b8e5810618a33d900ad6c19eb30b290b97/fonttools-4.61.1-py3-none-any.whl", hash = "sha256:17d2bf5d541add43822bcf0c43d7d847b160c9bb01d15d5007d84e2217aaa371", size = 1148996, upload-time = "2025-12-12T17:31:21.03Z" },
]

[package.optional-dependencies]
woff = [
    { name = "brotli", marker = "platform_python_implementation == 'CPython'" },
    { name = "brotlicffi", marker = "platform_python_implementation != 'CPython'" },
    { name = "zopfli" },
]

[[package]]
name = "gunicorn"
version = "23.0.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "packaging" },
]
sdist = { url = "https://files.pythonhosted.org/packages/34/72/9614c465dc206155d93eff0ca20d42e1e35afc533971379482de953521a4/gunicorn-23.0.0.tar.gz", hash = "sha256:f014447a0101dc57e294f6c18ca6b40227a4c90e9bdb586042628030cba004ec", size = 375031, upload-time = "2024-08-10T20:25:27.378Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/cb/7d/6dac2a6e1eba33ee43f318edbed4ff29151a49b5d37f080aad1e6469bca4/gunicorn-23.0.0-py3-none-any.whl", hash = "sha256:ec400d38950de4dfd418cff8328b2c8faed0edb0d517d3394e457c317908ca4d", size = 85029, upload-time = "2024-08-10T20:25:24.996Z" },
]

[[package]]
name = "idna"
version = "3.11"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/6f/6d/0703ccc57f3a7233505399edb88de3cbd678da106337b9fcde432b65ed60/idna-3.11.tar.gz", hash = "sha256:795dafcc9c04ed0c1fb032c2aa73654d8e8c5023a7df64a53f39190ada629902", size = 194582, upload-time = "2025-10-12T14:55:20.501Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/0e/61/66938bbb5fc52dbdf84594873d5b51fb1f7c7794e9c0f5bd885f30bc507b/idna-3.11-py3-none-any.whl", hash = "sha256:771a87f49d9defaf64091e6e6fe9c18d4833f140bd19464795bc32d966ca37ea", size = 71008, upload-time = "2025-10-12T14:55:18.883Z" },
]

[[package]]
name = "inflection"
version = "0.5.1"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/e1/7e/691d061b7329bc8d54edbf0ec22fbfb2afe61facb681f9aaa9bff7a27d04/inflection-0.5.1.tar.gz", hash = "sha256:1a29730d366e996aaacffb2f1f1cb9593dc38e2ddd30c91250c6dde09ea9b417", size = 15091, upload-time = "2020-08-22T08:16:29.139Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/59/91/aa6bde563e0085a02a435aa99b49ef75b0a4b062635e606dab23ce18d720/inflection-0.5.1-py2.py3-none-any.whl", hash = "sha256:f38b2b640938a4f35ade69ac3d053042959b62a0f1076a5bbaa1b9526605a8a2", size = 9454, upload-time = "2020-08-22T08:16:27.816Z" },
]

[[package]]
name = "iniconfig"
version = "2.3.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/72/34/14ca021ce8e5dfedc35312d08ba8bf51fdd999c576889fc2c24cb97f4f10/iniconfig-2.3.0.tar.gz", hash = "sha256:c76315c77db068650d49c5b56314774a7804df16fee4402c1f19d6d15d8c4730", size = 20503, upload-time = "2025-10-18T21:55:43.219Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/cb/b1/3846dd7f199d53cb17f49cba7e651e9ce294d8497c8c150530ed11865bb8/iniconfig-2.3.0-py3-none-any.whl", hash = "sha256:f631c04d2c48c52b84d0d0549c99ff3859c98df65b3101406327ecc7d53fbf12", size = 7484, upload-time = "2025-10-18T21:55:41.639Z" },
]

[[package]]
name = "isort"
version = "7.0.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/63/53/4f3c058e3bace40282876f9b553343376ee687f3c35a525dc79dbd450f88/isort-7.0.0.tar.gz", hash = "sha256:5513527951aadb3ac4292a41a16cbc50dd1642432f5e8c20057d414bdafb4187", size = 805049, upload-time = "2025-10-11T13:30:59.107Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/7f/ed/e3705d6d02b4f7aea715a353c8ce193efd0b5db13e204df895d38734c244/isort-7.0.0-py3-none-any.whl", hash = "sha256:1bcabac8bc3c36c7fb7b98a76c8abb18e0f841a3ba81decac7691008592499c1", size = 94672, upload-time = "2025-10-11T13:30:57.665Z" },
]

[[package]]
name = "jsonschema"
version = "4.25.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "attrs" },
    { name = "jsonschema-specifications" },
    { name = "referencing" },
    { name = "rpds-py" },
]
sdist = { url = "https://files.pythonhosted.org/packages/74/69/f7185de793a29082a9f3c7728268ffb31cb5095131a9c139a74078e27336/jsonschema-4.25.1.tar.gz", hash = "sha256:e4a9655ce0da0c0b67a085847e00a3a51449e1157f4f75e9fb5aa545e122eb85", size = 357342, upload-time = "2025-08-18T17:03:50.038Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/bf/9c/8c95d856233c1f82500c2450b8c68576b4cf1c871db3afac5c34ff84e6fd/jsonschema-4.25.1-py3-none-any.whl", hash = "sha256:3fba0169e345c7175110351d456342c364814cfcf3b964ba4587f22915230a63", size = 90040, upload-time = "2025-08-18T17:03:48.373Z" },
]

[[package]]
name = "jsonschema-specifications"
version = "2025.9.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "referencing" },
]
sdist = { url = "https://files.pythonhosted.org/packages/19/74/a633ee74eb36c44aa6d1095e7cc5569bebf04342ee146178e2d36600708b/jsonschema_specifications-2025.9.1.tar.gz", hash = "sha256:b540987f239e745613c7a9176f3edb72b832a4ac465cf02712288397832b5e8d", size = 32855, upload-time = "2025-09-08T01:34:59.186Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/41/45/1a4ed80516f02155c51f51e8cedb3c1902296743db0bbc66608a0db2814f/jsonschema_specifications-2025.9.1-py3-none-any.whl", hash = "sha256:98802fee3a11ee76ecaca44429fda8a41bff98b00a0f2838151b113f210cc6fe", size = 18437, upload-time = "2025-09-08T01:34:57.871Z" },
]

[[package]]
name = "kombu"
version = "5.6.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "amqp" },
    { name = "packaging" },
    { name = "tzdata" },
    { name = "vine" },
]
sdist = { url = "https://files.pythonhosted.org/packages/ac/05/749ada8e51718445d915af13f1d18bc4333848e8faa0cb234028a3328ec8/kombu-5.6.1.tar.gz", hash = "sha256:90f1febb57ad4f53ca327a87598191b2520e0c793c75ea3b88d98e3b111282e4", size = 471548, upload-time = "2025-11-25T11:07:33.504Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/14/d6/943cf84117cd9ddecf6e1707a3f712a49fc64abdb8ac31b19132871af1dd/kombu-5.6.1-py3-none-any.whl", hash = "sha256:b69e3f5527ec32fc5196028a36376501682973e9620d6175d1c3d4eaf7e95409", size = 214141, upload-time = "2025-11-25T11:07:31.54Z" },
]

[[package]]
name = "mccabe"
version = "0.7.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/e7/ff/0ffefdcac38932a54d2b5eed4e0ba8a408f215002cd178ad1df0f2806ff8/mccabe-0.7.0.tar.gz", hash = "sha256:348e0240c33b60bbdf4e523192ef919f28cb2c3d7d5c7794f74009290f236325", size = 9658, upload-time = "2022-01-24T01:14:51.113Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/27/1a/1f68f9ba0c207934b35b86a8ca3aad8395a3d6dd7921c0686e23853ff5a9/mccabe-0.7.0-py2.py3-none-any.whl", hash = "sha256:6c2d30ab6be0e4a46919781807b4f0d834ebdd6c6e3dca0bda5a15f863427b6e", size = 7350, upload-time = "2022-01-24T01:14:49.62Z" },
]

[[package]]
name = "mypy-extensions"
version = "1.1.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/a2/6e/371856a3fb9d31ca8dac321cda606860fa4548858c0cc45d9d1d4ca2628b/mypy_extensions-1.1.0.tar.gz", hash = "sha256:52e68efc3284861e772bbcd66823fde5ae21fd2fdb51c62a211403730b916558", size = 6343, upload-time = "2025-04-22T14:54:24.164Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/79/7b/2c79738432f5c924bef5071f933bcc9efd0473bac3b4aa584a6f7c1c8df8/mypy_extensions-1.1.0-py3-none-any.whl", hash = "sha256:1be4cccdb0f2482337c4743e60421de3a356cd97508abadd57d47403e94f5505", size = 4963, upload-time = "2025-04-22T14:54:22.983Z" },
]

[[package]]
name = "packaging"
version = "25.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/a1/d4/1fc4078c65507b51b96ca8f8c3ba19e6a61c8253c72794544580a7b6c24d/packaging-25.0.tar.gz", hash = "sha256:d443872c98d677bf60f6a1f2f8c1cb748e8fe762d2bf9d3148b5599295b0fc4f", size = 165727, upload-time = "2025-04-19T11:48:59.673Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/20/12/38679034af332785aac8774540895e234f4d07f7545804097de4b666afd8/packaging-25.0-py3-none-any.whl", hash = "sha256:29572ef2b1f17581046b3a2227d5c611fb25ec70ca1ba8554b24b0e69331a484", size = 66469, upload-time = "2025-04-19T11:48:57.875Z" },
]

[[package]]
name = "pathspec"
version = "0.12.1"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/ca/bc/f35b8446f4531a7cb215605d100cd88b7ac6f44ab3fc94870c120ab3adbf/pathspec-0.12.1.tar.gz", hash = "sha256:a482d51503a1ab33b1c67a6c3813a26953dbdc71c31dacaef9a838c4e29f5712", size = 51043, upload-time = "2023-12-10T22:30:45Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/cc/20/ff623b09d963f88bfde16306a54e12ee5ea43e9b597108672ff3a408aad6/pathspec-0.12.1-py3-none-any.whl", hash = "sha256:a0d503e138a4c123b27490a4f7beda6a01c6f288df0e4a8b79c7eb0dc7b4cc08", size = 31191, upload-time = "2023-12-10T22:30:43.14Z" },
]

[[package]]
name = "pillow"
version = "12.0.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/5a/b0/cace85a1b0c9775a9f8f5d5423c8261c858760e2466c79b2dd184638b056/pillow-12.0.0.tar.gz", hash = "sha256:87d4f8125c9988bfbed67af47dd7a953e2fc7b0cc1e7800ec6d2080d490bb353", size = 47008828, upload-time = "2025-10-15T18:24:14.008Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/2c/90/4fcce2c22caf044e660a198d740e7fbc14395619e3cb1abad12192c0826c/pillow-12.0.0-cp312-cp312-macosx_10_13_x86_64.whl", hash = "sha256:53561a4ddc36facb432fae7a9d8afbfaf94795414f5cdc5fc52f28c1dca90371", size = 5249377, upload-time = "2025-10-15T18:22:05.993Z" },
    { url = "https://files.pythonhosted.org/packages/fd/e0/ed960067543d080691d47d6938ebccbf3976a931c9567ab2fbfab983a5dd/pillow-12.0.0-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:71db6b4c1653045dacc1585c1b0d184004f0d7e694c7b34ac165ca70c0838082", size = 4650343, upload-time = "2025-10-15T18:22:07.718Z" },
    { url = "https://files.pythonhosted.org/packages/e7/a1/f81fdeddcb99c044bf7d6faa47e12850f13cee0849537a7d27eeab5534d4/pillow-12.0.0-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:2fa5f0b6716fc88f11380b88b31fe591a06c6315e955c096c35715788b339e3f", size = 6232981, upload-time = "2025-10-15T18:22:09.287Z" },
    { url = "https://files.pythonhosted.org/packages/88/e1/9098d3ce341a8750b55b0e00c03f1630d6178f38ac191c81c97a3b047b44/pillow-12.0.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:82240051c6ca513c616f7f9da06e871f61bfd7805f566275841af15015b8f98d", size = 8041399, upload-time = "2025-10-15T18:22:10.872Z" },
    { url = "https://files.pythonhosted.org/packages/a7/62/a22e8d3b602ae8cc01446d0c57a54e982737f44b6f2e1e019a925143771d/pillow-12.0.0-cp312-cp312-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:55f818bd74fe2f11d4d7cbc65880a843c4075e0ac7226bc1a23261dbea531953", size = 6347740, upload-time = "2025-10-15T18:22:12.769Z" },
    { url = "https://files.pythonhosted.org/packages/4f/87/424511bdcd02c8d7acf9f65caa09f291a519b16bd83c3fb3374b3d4ae951/pillow-12.0.0-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:b87843e225e74576437fd5b6a4c2205d422754f84a06942cfaf1dc32243e45a8", size = 7040201, upload-time = "2025-10-15T18:22:14.813Z" },
    { url = "https://files.pythonhosted.org/packages/dc/4d/435c8ac688c54d11755aedfdd9f29c9eeddf68d150fe42d1d3dbd2365149/pillow-12.0.0-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:c607c90ba67533e1b2355b821fef6764d1dd2cbe26b8c1005ae84f7aea25ff79", size = 6462334, upload-time = "2025-10-15T18:22:16.375Z" },
    { url = "https://files.pythonhosted.org/packages/2b/f2/ad34167a8059a59b8ad10bc5c72d4d9b35acc6b7c0877af8ac885b5f2044/pillow-12.0.0-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:21f241bdd5080a15bc86d3466a9f6074a9c2c2b314100dd896ac81ee6db2f1ba", size = 7134162, upload-time = "2025-10-15T18:22:17.996Z" },
    { url = "https://files.pythonhosted.org/packages/0c/b1/a7391df6adacf0a5c2cf6ac1cf1fcc1369e7d439d28f637a847f8803beb3/pillow-12.0.0-cp312-cp312-win32.whl", hash = "sha256:dd333073e0cacdc3089525c7df7d39b211bcdf31fc2824e49d01c6b6187b07d0", size = 6298769, upload-time = "2025-10-15T18:22:19.923Z" },
    { url = "https://files.pythonhosted.org/packages/a2/0b/d87733741526541c909bbf159e338dcace4f982daac6e5a8d6be225ca32d/pillow-12.0.0-cp312-cp312-win_amd64.whl", hash = "sha256:9fe611163f6303d1619bbcb653540a4d60f9e55e622d60a3108be0d5b441017a", size = 7001107, upload-time = "2025-10-15T18:22:21.644Z" },
    { url = "https://files.pythonhosted.org/packages/bc/96/aaa61ce33cc98421fb6088af2a03be4157b1e7e0e87087c888e2370a7f45/pillow-12.0.0-cp312-cp312-win_arm64.whl", hash = "sha256:7dfb439562f234f7d57b1ac6bc8fe7f838a4bd49c79230e0f6a1da93e82f1fad", size = 2436012, upload-time = "2025-10-15T18:22:23.621Z" },
    { url = "https://files.pythonhosted.org/packages/62/f2/de993bb2d21b33a98d031ecf6a978e4b61da207bef02f7b43093774c480d/pillow-12.0.0-cp313-cp313-ios_13_0_arm64_iphoneos.whl", hash = "sha256:0869154a2d0546545cde61d1789a6524319fc1897d9ee31218eae7a60ccc5643", size = 4045493, upload-time = "2025-10-15T18:22:25.758Z" },
    { url = "https://files.pythonhosted.org/packages/0e/b6/bc8d0c4c9f6f111a783d045310945deb769b806d7574764234ffd50bc5ea/pillow-12.0.0-cp313-cp313-ios_13_0_arm64_iphonesimulator.whl", hash = "sha256:a7921c5a6d31b3d756ec980f2f47c0cfdbce0fc48c22a39347a895f41f4a6ea4", size = 4120461, upload-time = "2025-10-15T18:22:27.286Z" },
    { url = "https://files.pythonhosted.org/packages/5d/57/d60d343709366a353dc56adb4ee1e7d8a2cc34e3fbc22905f4167cfec119/pillow-12.0.0-cp313-cp313-ios_13_0_x86_64_iphonesimulator.whl", hash = "sha256:1ee80a59f6ce048ae13cda1abf7fbd2a34ab9ee7d401c46be3ca685d1999a399", size = 3576912, upload-time = "2025-10-15T18:22:28.751Z" },
    { url = "https://files.pythonhosted.org/packages/a4/a4/a0a31467e3f83b94d37568294b01d22b43ae3c5d85f2811769b9c66389dd/pillow-12.0.0-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:c50f36a62a22d350c96e49ad02d0da41dbd17ddc2e29750dbdba4323f85eb4a5", size = 5249132, upload-time = "2025-10-15T18:22:30.641Z" },
    { url = "https://files.pythonhosted.org/packages/83/06/48eab21dd561de2914242711434c0c0eb992ed08ff3f6107a5f44527f5e9/pillow-12.0.0-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:5193fde9a5f23c331ea26d0cf171fbf67e3f247585f50c08b3e205c7aeb4589b", size = 4650099, upload-time = "2025-10-15T18:22:32.73Z" },
    { url = "https://files.pythonhosted.org/packages/fc/bd/69ed99fd46a8dba7c1887156d3572fe4484e3f031405fcc5a92e31c04035/pillow-12.0.0-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:bde737cff1a975b70652b62d626f7785e0480918dece11e8fef3c0cf057351c3", size = 6230808, upload-time = "2025-10-15T18:22:34.337Z" },
    { url = "https://files.pythonhosted.org/packages/ea/94/8fad659bcdbf86ed70099cb60ae40be6acca434bbc8c4c0d4ef356d7e0de/pillow-12.0.0-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:a6597ff2b61d121172f5844b53f21467f7082f5fb385a9a29c01414463f93b07", size = 8037804, upload-time = "2025-10-15T18:22:36.402Z" },
    { url = "https://files.pythonhosted.org/packages/20/39/c685d05c06deecfd4e2d1950e9a908aa2ca8bc4e6c3b12d93b9cafbd7837/pillow-12.0.0-cp313-cp313-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:0b817e7035ea7f6b942c13aa03bb554fc44fea70838ea21f8eb31c638326584e", size = 6345553, upload-time = "2025-10-15T18:22:38.066Z" },
    { url = "https://files.pythonhosted.org/packages/38/57/755dbd06530a27a5ed74f8cb0a7a44a21722ebf318edbe67ddbd7fb28f88/pillow-12.0.0-cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:f4f1231b7dec408e8670264ce63e9c71409d9583dd21d32c163e25213ee2a344", size = 7037729, upload-time = "2025-10-15T18:22:39.769Z" },
    { url = "https://files.pythonhosted.org/packages/ca/b6/7e94f4c41d238615674d06ed677c14883103dce1c52e4af16f000338cfd7/pillow-12.0.0-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:6e51b71417049ad6ab14c49608b4a24d8fb3fe605e5dfabfe523b58064dc3d27", size = 6459789, upload-time = "2025-10-15T18:22:41.437Z" },
    { url = "https://files.pythonhosted.org/packages/9c/14/4448bb0b5e0f22dd865290536d20ec8a23b64e2d04280b89139f09a36bb6/pillow-12.0.0-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:d120c38a42c234dc9a8c5de7ceaaf899cf33561956acb4941653f8bdc657aa79", size = 7130917, upload-time = "2025-10-15T18:22:43.152Z" },
    { url = "https://files.pythonhosted.org/packages/dd/ca/16c6926cc1c015845745d5c16c9358e24282f1e588237a4c36d2b30f182f/pillow-12.0.0-cp313-cp313-win32.whl", hash = "sha256:4cc6b3b2efff105c6a1656cfe59da4fdde2cda9af1c5e0b58529b24525d0a098", size = 6302391, upload-time = "2025-10-15T18:22:44.753Z" },
    { url = "https://files.pythonhosted.org/packages/6d/2a/dd43dcfd6dae9b6a49ee28a8eedb98c7d5ff2de94a5d834565164667b97b/pillow-12.0.0-cp313-cp313-win_amd64.whl", hash = "sha256:4cf7fed4b4580601c4345ceb5d4cbf5a980d030fd5ad07c4d2ec589f95f09905", size = 7007477, upload-time = "2025-10-15T18:22:46.838Z" },
    { url = "https://files.pythonhosted.org/packages/77/f0/72ea067f4b5ae5ead653053212af05ce3705807906ba3f3e8f58ddf617e6/pillow-12.0.0-cp313-cp313-win_arm64.whl", hash = "sha256:9f0b04c6b8584c2c193babcccc908b38ed29524b29dd464bc8801bf10d746a3a", size = 2435918, upload-time = "2025-10-15T18:22:48.399Z" },
    { url = "https://files.pythonhosted.org/packages/f5/5e/9046b423735c21f0487ea6cb5b10f89ea8f8dfbe32576fe052b5ba9d4e5b/pillow-12.0.0-cp313-cp313t-macosx_10_13_x86_64.whl", hash = "sha256:7fa22993bac7b77b78cae22bad1e2a987ddf0d9015c63358032f84a53f23cdc3", size = 5251406, upload-time = "2025-10-15T18:22:49.905Z" },
    { url = "https://files.pythonhosted.org/packages/12/66/982ceebcdb13c97270ef7a56c3969635b4ee7cd45227fa707c94719229c5/pillow-12.0.0-cp313-cp313t-macosx_11_0_arm64.whl", hash = "sha256:f135c702ac42262573fe9714dfe99c944b4ba307af5eb507abef1667e2cbbced", size = 4653218, upload-time = "2025-10-15T18:22:51.587Z" },
    { url = "https://files.pythonhosted.org/packages/16/b3/81e625524688c31859450119bf12674619429cab3119eec0e30a7a1029cb/pillow-12.0.0-cp313-cp313t-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:c85de1136429c524e55cfa4e033b4a7940ac5c8ee4d9401cc2d1bf48154bbc7b", size = 6266564, upload-time = "2025-10-15T18:22:53.215Z" },
    { url = "https://files.pythonhosted.org/packages/98/59/dfb38f2a41240d2408096e1a76c671d0a105a4a8471b1871c6902719450c/pillow-12.0.0-cp313-cp313t-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:38df9b4bfd3db902c9c2bd369bcacaf9d935b2fff73709429d95cc41554f7b3d", size = 8069260, upload-time = "2025-10-15T18:22:54.933Z" },
    { url = "https://files.pythonhosted.org/packages/dc/3d/378dbea5cd1874b94c312425ca77b0f47776c78e0df2df751b820c8c1d6c/pillow-12.0.0-cp313-cp313t-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:7d87ef5795da03d742bf49439f9ca4d027cde49c82c5371ba52464aee266699a", size = 6379248, upload-time = "2025-10-15T18:22:56.605Z" },
    { url = "https://files.pythonhosted.org/packages/84/b0/d525ef47d71590f1621510327acec75ae58c721dc071b17d8d652ca494d8/pillow-12.0.0-cp313-cp313t-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:aff9e4d82d082ff9513bdd6acd4f5bd359f5b2c870907d2b0a9c5e10d40c88fe", size = 7066043, upload-time = "2025-10-15T18:22:58.53Z" },
    { url = "https://files.pythonhosted.org/packages/61/2c/aced60e9cf9d0cde341d54bf7932c9ffc33ddb4a1595798b3a5150c7ec4e/pillow-12.0.0-cp313-cp313t-musllinux_1_2_aarch64.whl", hash = "sha256:8d8ca2b210ada074d57fcee40c30446c9562e542fc46aedc19baf758a93532ee", size = 6490915, upload-time = "2025-10-15T18:23:00.582Z" },
    { url = "https://files.pythonhosted.org/packages/ef/26/69dcb9b91f4e59f8f34b2332a4a0a951b44f547c4ed39d3e4dcfcff48f89/pillow-12.0.0-cp313-cp313t-musllinux_1_2_x86_64.whl", hash = "sha256:99a7f72fb6249302aa62245680754862a44179b545ded638cf1fef59befb57ef", size = 7157998, upload-time = "2025-10-15T18:23:02.627Z" },
    { url = "https://files.pythonhosted.org/packages/61/2b/726235842220ca95fa441ddf55dd2382b52ab5b8d9c0596fe6b3f23dafe8/pillow-12.0.0-cp313-cp313t-win32.whl", hash = "sha256:4078242472387600b2ce8d93ade8899c12bf33fa89e55ec89fe126e9d6d5d9e9", size = 6306201, upload-time = "2025-10-15T18:23:04.709Z" },
    { url = "https://files.pythonhosted.org/packages/c0/3d/2afaf4e840b2df71344ababf2f8edd75a705ce500e5dc1e7227808312ae1/pillow-12.0.0-cp313-cp313t-win_amd64.whl", hash = "sha256:2c54c1a783d6d60595d3514f0efe9b37c8808746a66920315bfd34a938d7994b", size = 7013165, upload-time = "2025-10-15T18:23:06.46Z" },
    { url = "https://files.pythonhosted.org/packages/6f/75/3fa09aa5cf6ed04bee3fa575798ddf1ce0bace8edb47249c798077a81f7f/pillow-12.0.0-cp313-cp313t-win_arm64.whl", hash = "sha256:26d9f7d2b604cd23aba3e9faf795787456ac25634d82cd060556998e39c6fa47", size = 2437834, upload-time = "2025-10-15T18:23:08.194Z" },
    { url = "https://files.pythonhosted.org/packages/54/2a/9a8c6ba2c2c07b71bec92cf63e03370ca5e5f5c5b119b742bcc0cde3f9c5/pillow-12.0.0-cp314-cp314-ios_13_0_arm64_iphoneos.whl", hash = "sha256:beeae3f27f62308f1ddbcfb0690bf44b10732f2ef43758f169d5e9303165d3f9", size = 4045531, upload-time = "2025-10-15T18:23:10.121Z" },
    { url = "https://files.pythonhosted.org/packages/84/54/836fdbf1bfb3d66a59f0189ff0b9f5f666cee09c6188309300df04ad71fa/pillow-12.0.0-cp314-cp314-ios_13_0_arm64_iphonesimulator.whl", hash = "sha256:d4827615da15cd59784ce39d3388275ec093ae3ee8d7f0c089b76fa87af756c2", size = 4120554, upload-time = "2025-10-15T18:23:12.14Z" },
    { url = "https://files.pythonhosted.org/packages/0d/cd/16aec9f0da4793e98e6b54778a5fbce4f375c6646fe662e80600b8797379/pillow-12.0.0-cp314-cp314-ios_13_0_x86_64_iphonesimulator.whl", hash = "sha256:3e42edad50b6909089750e65c91aa09aaf1e0a71310d383f11321b27c224ed8a", size = 3576812, upload-time = "2025-10-15T18:23:13.962Z" },
    { url = "https://files.pythonhosted.org/packages/f6/b7/13957fda356dc46339298b351cae0d327704986337c3c69bb54628c88155/pillow-12.0.0-cp314-cp314-macosx_10_15_x86_64.whl", hash = "sha256:e5d8efac84c9afcb40914ab49ba063d94f5dbdf5066db4482c66a992f47a3a3b", size = 5252689, upload-time = "2025-10-15T18:23:15.562Z" },
    { url = "https://files.pythonhosted.org/packages/fc/f5/eae31a306341d8f331f43edb2e9122c7661b975433de5e447939ae61c5da/pillow-12.0.0-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:266cd5f2b63ff316d5a1bba46268e603c9caf5606d44f38c2873c380950576ad", size = 4650186, upload-time = "2025-10-15T18:23:17.379Z" },
    { url = "https://files.pythonhosted.org/packages/86/62/2a88339aa40c4c77e79108facbd307d6091e2c0eb5b8d3cf4977cfca2fe6/pillow-12.0.0-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:58eea5ebe51504057dd95c5b77d21700b77615ab0243d8152793dc00eb4faf01", size = 6230308, upload-time = "2025-10-15T18:23:18.971Z" },
    { url = "https://files.pythonhosted.org/packages/c7/33/5425a8992bcb32d1cb9fa3dd39a89e613d09a22f2c8083b7bf43c455f760/pillow-12.0.0-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:f13711b1a5ba512d647a0e4ba79280d3a9a045aaf7e0cc6fbe96b91d4cdf6b0c", size = 8039222, upload-time = "2025-10-15T18:23:20.909Z" },
    { url = "https://files.pythonhosted.org/packages/d8/61/3f5d3b35c5728f37953d3eec5b5f3e77111949523bd2dd7f31a851e50690/pillow-12.0.0-cp314-cp314-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:6846bd2d116ff42cba6b646edf5bf61d37e5cbd256425fa089fee4ff5c07a99e", size = 6346657, upload-time = "2025-10-15T18:23:23.077Z" },
    { url = "https://files.pythonhosted.org/packages/3a/be/ee90a3d79271227e0f0a33c453531efd6ed14b2e708596ba5dd9be948da3/pillow-12.0.0-cp314-cp314-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:c98fa880d695de164b4135a52fd2e9cd7b7c90a9d8ac5e9e443a24a95ef9248e", size = 7038482, upload-time = "2025-10-15T18:23:25.005Z" },
    { url = "https://files.pythonhosted.org/packages/44/34/a16b6a4d1ad727de390e9bd9f19f5f669e079e5826ec0f329010ddea492f/pillow-12.0.0-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:fa3ed2a29a9e9d2d488b4da81dcb54720ac3104a20bf0bd273f1e4648aff5af9", size = 6461416, upload-time = "2025-10-15T18:23:27.009Z" },
    { url = "https://files.pythonhosted.org/packages/b6/39/1aa5850d2ade7d7ba9f54e4e4c17077244ff7a2d9e25998c38a29749eb3f/pillow-12.0.0-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:d034140032870024e6b9892c692fe2968493790dd57208b2c37e3fb35f6df3ab", size = 7131584, upload-time = "2025-10-15T18:23:29.752Z" },
    { url = "https://files.pythonhosted.org/packages/bf/db/4fae862f8fad0167073a7733973bfa955f47e2cac3dc3e3e6257d10fab4a/pillow-12.0.0-cp314-cp314-win32.whl", hash = "sha256:1b1b133e6e16105f524a8dec491e0586d072948ce15c9b914e41cdadd209052b", size = 6400621, upload-time = "2025-10-15T18:23:32.06Z" },
    { url = "https://files.pythonhosted.org/packages/2b/24/b350c31543fb0107ab2599464d7e28e6f856027aadda995022e695313d94/pillow-12.0.0-cp314-cp314-win_amd64.whl", hash = "sha256:8dc232e39d409036af549c86f24aed8273a40ffa459981146829a324e0848b4b", size = 7142916, upload-time = "2025-10-15T18:23:34.71Z" },
    { url = "https://files.pythonhosted.org/packages/0f/9b/0ba5a6fd9351793996ef7487c4fdbde8d3f5f75dbedc093bb598648fddf0/pillow-12.0.0-cp314-cp314-win_arm64.whl", hash = "sha256:d52610d51e265a51518692045e372a4c363056130d922a7351429ac9f27e70b0", size = 2523836, upload-time = "2025-10-15T18:23:36.967Z" },
    { url = "https://files.pythonhosted.org/packages/f5/7a/ceee0840aebc579af529b523d530840338ecf63992395842e54edc805987/pillow-12.0.0-cp314-cp314t-macosx_10_15_x86_64.whl", hash = "sha256:1979f4566bb96c1e50a62d9831e2ea2d1211761e5662afc545fa766f996632f6", size = 5255092, upload-time = "2025-10-15T18:23:38.573Z" },
    { url = "https://files.pythonhosted.org/packages/44/76/20776057b4bfd1aef4eeca992ebde0f53a4dce874f3ae693d0ec90a4f79b/pillow-12.0.0-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:b2e4b27a6e15b04832fe9bf292b94b5ca156016bbc1ea9c2c20098a0320d6cf6", size = 4653158, upload-time = "2025-10-15T18:23:40.238Z" },
    { url = "https://files.pythonhosted.org/packages/82/3f/d9ff92ace07be8836b4e7e87e6a4c7a8318d47c2f1463ffcf121fc57d9cb/pillow-12.0.0-cp314-cp314t-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:fb3096c30df99fd01c7bf8e544f392103d0795b9f98ba71a8054bcbf56b255f1", size = 6267882, upload-time = "2025-10-15T18:23:42.434Z" },
    { url = "https://files.pythonhosted.org/packages/9f/7a/4f7ff87f00d3ad33ba21af78bfcd2f032107710baf8280e3722ceec28cda/pillow-12.0.0-cp314-cp314t-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:7438839e9e053ef79f7112c881cef684013855016f928b168b81ed5835f3e75e", size = 8071001, upload-time = "2025-10-15T18:23:44.29Z" },
    { url = "https://files.pythonhosted.org/packages/75/87/fcea108944a52dad8cca0715ae6247e271eb80459364a98518f1e4f480c1/pillow-12.0.0-cp314-cp314t-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:5d5c411a8eaa2299322b647cd932586b1427367fd3184ffbb8f7a219ea2041ca", size = 6380146, upload-time = "2025-10-15T18:23:46.065Z" },
    { url = "https://files.pythonhosted.org/packages/91/52/0d31b5e571ef5fd111d2978b84603fce26aba1b6092f28e941cb46570745/pillow-12.0.0-cp314-cp314t-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:d7e091d464ac59d2c7ad8e7e08105eaf9dafbc3883fd7265ffccc2baad6ac925", size = 7067344, upload-time = "2025-10-15T18:23:47.898Z" },
    { url = "https://files.pythonhosted.org/packages/7b/f4/2dd3d721f875f928d48e83bb30a434dee75a2531bca839bb996bb0aa5a91/pillow-12.0.0-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:792a2c0be4dcc18af9d4a2dfd8a11a17d5e25274a1062b0ec1c2d79c76f3e7f8", size = 6491864, upload-time = "2025-10-15T18:23:49.607Z" },
    { url = "https://files.pythonhosted.org/packages/30/4b/667dfcf3d61fc309ba5a15b141845cece5915e39b99c1ceab0f34bf1d124/pillow-12.0.0-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:afbefa430092f71a9593a99ab6a4e7538bc9eabbf7bf94f91510d3503943edc4", size = 7158911, upload-time = "2025-10-15T18:23:51.351Z" },
    { url = "https://files.pythonhosted.org/packages/a2/2f/16cabcc6426c32218ace36bf0d55955e813f2958afddbf1d391849fee9d1/pillow-12.0.0-cp314-cp314t-win32.whl", hash = "sha256:3830c769decf88f1289680a59d4f4c46c72573446352e2befec9a8512104fa52", size = 6408045, upload-time = "2025-10-15T18:23:53.177Z" },
    { url = "https://files.pythonhosted.org/packages/35/73/e29aa0c9c666cf787628d3f0dcf379f4791fba79f4936d02f8b37165bdf8/pillow-12.0.0-cp314-cp314t-win_amd64.whl", hash = "sha256:905b0365b210c73afb0ebe9101a32572152dfd1c144c7e28968a331b9217b94a", size = 7148282, upload-time = "2025-10-15T18:23:55.316Z" },
    { url = "https://files.pythonhosted.org/packages/c1/70/6b41bdcddf541b437bbb9f47f94d2db5d9ddef6c37ccab8c9107743748a4/pillow-12.0.0-cp314-cp314t-win_arm64.whl", hash = "sha256:99353a06902c2e43b43e8ff74ee65a7d90307d82370604746738a1e0661ccca7", size = 2525630, upload-time = "2025-10-15T18:23:57.149Z" },
]

[[package]]
name = "platformdirs"
version = "4.5.1"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/cf/86/0248f086a84f01b37aaec0fa567b397df1a119f73c16f6c7a9aac73ea309/platformdirs-4.5.1.tar.gz", hash = "sha256:61d5cdcc6065745cdd94f0f878977f8de9437be93de97c1c12f853c9c0cdcbda", size = 21715, upload-time = "2025-12-05T13:52:58.638Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/cb/28/3bfe2fa5a7b9c46fe7e13c97bda14c895fb10fa2ebf1d0abb90e0cea7ee1/platformdirs-4.5.1-py3-none-any.whl", hash = "sha256:d03afa3963c806a9bed9d5125c8f4cb2fdaf74a55ab60e5d59b3fde758104d31", size = 18731, upload-time = "2025-12-05T13:52:56.823Z" },
]

[[package]]
name = "pluggy"
version = "1.6.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/f9/e2/3e91f31a7d2b083fe6ef3fa267035b518369d9511ffab804f839851d2779/pluggy-1.6.0.tar.gz", hash = "sha256:7dcc130b76258d33b90f61b658791dede3486c3e6bfb003ee5c9bfb396dd22f3", size = 69412, upload-time = "2025-05-15T12:30:07.975Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/54/20/4d324d65cc6d9205fabedc306948156824eb9f0ee1633355a8f7ec5c66bf/pluggy-1.6.0-py3-none-any.whl", hash = "sha256:e920276dd6813095e9377c0bc5566d94c932c33b27a3e3945d8389c374dd4746", size = 20538, upload-time = "2025-05-15T12:30:06.134Z" },
]

[[package]]
name = "prompt-toolkit"
version = "3.0.52"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "wcwidth" },
]
sdist = { url = "https://files.pythonhosted.org/packages/a1/96/06e01a7b38dce6fe1db213e061a4602dd6032a8a97ef6c1a862537732421/prompt_toolkit-3.0.52.tar.gz", hash = "sha256:28cde192929c8e7321de85de1ddbe736f1375148b02f2e17edd840042b1be855", size = 434198, upload-time = "2025-08-27T15:24:02.057Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/84/03/0d3ce49e2505ae70cf43bc5bb3033955d2fc9f932163e84dc0779cc47f48/prompt_toolkit-3.0.52-py3-none-any.whl", hash = "sha256:9aac639a3bbd33284347de5ad8d68ecc044b91a762dc39b7c21095fcd6a19955", size = 391431, upload-time = "2025-08-27T15:23:59.498Z" },
]

[[package]]
name = "psycopg2-binary"
version = "2.9.11"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/ac/6c/8767aaa597ba424643dc87348c6f1754dd9f48e80fdc1b9f7ca5c3a7c213/psycopg2-binary-2.9.11.tar.gz", hash = "sha256:b6aed9e096bf63f9e75edf2581aa9a7e7186d97ab5c177aa6c87797cd591236c", size = 379620, upload-time = "2025-10-10T11:14:48.041Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/d8/91/f870a02f51be4a65987b45a7de4c2e1897dd0d01051e2b559a38fa634e3e/psycopg2_binary-2.9.11-cp312-cp312-macosx_10_13_x86_64.whl", hash = "sha256:be9b840ac0525a283a96b556616f5b4820e0526addb8dcf6525a0fa162730be4", size = 3756603, upload-time = "2025-10-10T11:11:52.213Z" },
    { url = "https://files.pythonhosted.org/packages/27/fa/cae40e06849b6c9a95eb5c04d419942f00d9eaac8d81626107461e268821/psycopg2_binary-2.9.11-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:f090b7ddd13ca842ebfe301cd587a76a4cf0913b1e429eb92c1be5dbeb1a19bc", size = 3864509, upload-time = "2025-10-10T11:11:56.452Z" },
    { url = "https://files.pythonhosted.org/packages/2d/75/364847b879eb630b3ac8293798e380e441a957c53657995053c5ec39a316/psycopg2_binary-2.9.11-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:ab8905b5dcb05bf3fb22e0cf90e10f469563486ffb6a96569e51f897c750a76a", size = 4411159, upload-time = "2025-10-10T11:12:00.49Z" },
    { url = "https://files.pythonhosted.org/packages/6f/a0/567f7ea38b6e1c62aafd58375665a547c00c608a471620c0edc364733e13/psycopg2_binary-2.9.11-cp312-cp312-manylinux2014_ppc64le.manylinux_2_17_ppc64le.whl", hash = "sha256:bf940cd7e7fec19181fdbc29d76911741153d51cab52e5c21165f3262125685e", size = 4468234, upload-time = "2025-10-10T11:12:04.892Z" },
    { url = "https://files.pythonhosted.org/packages/30/da/4e42788fb811bbbfd7b7f045570c062f49e350e1d1f3df056c3fb5763353/psycopg2_binary-2.9.11-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:fa0f693d3c68ae925966f0b14b8edda71696608039f4ed61b1fe9ffa468d16db", size = 4166236, upload-time = "2025-10-10T11:12:11.674Z" },
    { url = "https://files.pythonhosted.org/packages/3c/94/c1777c355bc560992af848d98216148be5f1be001af06e06fc49cbded578/psycopg2_binary-2.9.11-cp312-cp312-manylinux_2_38_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:a1cf393f1cdaf6a9b57c0a719a1068ba1069f022a59b8b1fe44b006745b59757", size = 3983083, upload-time = "2025-10-30T02:55:15.73Z" },
    { url = "https://files.pythonhosted.org/packages/bd/42/c9a21edf0e3daa7825ed04a4a8588686c6c14904344344a039556d78aa58/psycopg2_binary-2.9.11-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:ef7a6beb4beaa62f88592ccc65df20328029d721db309cb3250b0aae0fa146c3", size = 3652281, upload-time = "2025-10-10T11:12:17.713Z" },
    { url = "https://files.pythonhosted.org/packages/12/22/dedfbcfa97917982301496b6b5e5e6c5531d1f35dd2b488b08d1ebc52482/psycopg2_binary-2.9.11-cp312-cp312-musllinux_1_2_ppc64le.whl", hash = "sha256:31b32c457a6025e74d233957cc9736742ac5a6cb196c6b68499f6bb51390bd6a", size = 3298010, upload-time = "2025-10-10T11:12:22.671Z" },
    { url = "https://files.pythonhosted.org/packages/66/ea/d3390e6696276078bd01b2ece417deac954dfdd552d2edc3d03204416c0c/psycopg2_binary-2.9.11-cp312-cp312-musllinux_1_2_riscv64.whl", hash = "sha256:edcb3aeb11cb4bf13a2af3c53a15b3d612edeb6409047ea0b5d6a21a9d744b34", size = 3044641, upload-time = "2025-10-30T02:55:19.929Z" },
    { url = "https://files.pythonhosted.org/packages/12/9a/0402ded6cbd321da0c0ba7d34dc12b29b14f5764c2fc10750daa38e825fc/psycopg2_binary-2.9.11-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:62b6d93d7c0b61a1dd6197d208ab613eb7dcfdcca0a49c42ceb082257991de9d", size = 3347940, upload-time = "2025-10-10T11:12:26.529Z" },
    { url = "https://files.pythonhosted.org/packages/b1/d2/99b55e85832ccde77b211738ff3925a5d73ad183c0b37bcbbe5a8ff04978/psycopg2_binary-2.9.11-cp312-cp312-win_amd64.whl", hash = "sha256:b33fabeb1fde21180479b2d4667e994de7bbf0eec22832ba5d9b5e4cf65b6c6d", size = 2714147, upload-time = "2025-10-10T11:12:29.535Z" },
    { url = "https://files.pythonhosted.org/packages/ff/a8/a2709681b3ac11b0b1786def10006b8995125ba268c9a54bea6f5ae8bd3e/psycopg2_binary-2.9.11-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:b8fb3db325435d34235b044b199e56cdf9ff41223a4b9752e8576465170bb38c", size = 3756572, upload-time = "2025-10-10T11:12:32.873Z" },
    { url = "https://files.pythonhosted.org/packages/62/e1/c2b38d256d0dafd32713e9f31982a5b028f4a3651f446be70785f484f472/psycopg2_binary-2.9.11-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:366df99e710a2acd90efed3764bb1e28df6c675d33a7fb40df9b7281694432ee", size = 3864529, upload-time = "2025-10-10T11:12:36.791Z" },
    { url = "https://files.pythonhosted.org/packages/11/32/b2ffe8f3853c181e88f0a157c5fb4e383102238d73c52ac6d93a5c8bffe6/psycopg2_binary-2.9.11-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:8c55b385daa2f92cb64b12ec4536c66954ac53654c7f15a203578da4e78105c0", size = 4411242, upload-time = "2025-10-10T11:12:42.388Z" },
    { url = "https://files.pythonhosted.org/packages/10/04/6ca7477e6160ae258dc96f67c371157776564679aefd247b66f4661501a2/psycopg2_binary-2.9.11-cp313-cp313-manylinux2014_ppc64le.manylinux_2_17_ppc64le.whl", hash = "sha256:c0377174bf1dd416993d16edc15357f6eb17ac998244cca19bc67cdc0e2e5766", size = 4468258, upload-time = "2025-10-10T11:12:48.654Z" },
    { url = "https://files.pythonhosted.org/packages/3c/7e/6a1a38f86412df101435809f225d57c1a021307dd0689f7a5e7fe83588b1/psycopg2_binary-2.9.11-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:5c6ff3335ce08c75afaed19e08699e8aacf95d4a260b495a4a8545244fe2ceb3", size = 4166295, upload-time = "2025-10-10T11:12:52.525Z" },
    { url = "https://files.pythonhosted.org/packages/f2/7d/c07374c501b45f3579a9eb761cbf2604ddef3d96ad48679112c2c5aa9c25/psycopg2_binary-2.9.11-cp313-cp313-manylinux_2_38_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:84011ba3109e06ac412f95399b704d3d6950e386b7994475b231cf61eec2fc1f", size = 3983133, upload-time = "2025-10-30T02:55:24.329Z" },
    { url = "https://files.pythonhosted.org/packages/82/56/993b7104cb8345ad7d4516538ccf8f0d0ac640b1ebd8c754a7b024e76878/psycopg2_binary-2.9.11-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:ba34475ceb08cccbdd98f6b46916917ae6eeb92b5ae111df10b544c3a4621dc4", size = 3652383, upload-time = "2025-10-10T11:12:56.387Z" },
    { url = "https://files.pythonhosted.org/packages/2d/ac/eaeb6029362fd8d454a27374d84c6866c82c33bfc24587b4face5a8e43ef/psycopg2_binary-2.9.11-cp313-cp313-musllinux_1_2_ppc64le.whl", hash = "sha256:b31e90fdd0f968c2de3b26ab014314fe814225b6c324f770952f7d38abf17e3c", size = 3298168, upload-time = "2025-10-10T11:13:00.403Z" },
    { url = "https://files.pythonhosted.org/packages/2b/39/50c3facc66bded9ada5cbc0de867499a703dc6bca6be03070b4e3b65da6c/psycopg2_binary-2.9.11-cp313-cp313-musllinux_1_2_riscv64.whl", hash = "sha256:d526864e0f67f74937a8fce859bd56c979f5e2ec57ca7c627f5f1071ef7fee60", size = 3044712, upload-time = "2025-10-30T02:55:27.975Z" },
    { url = "https://files.pythonhosted.org/packages/9c/8e/b7de019a1f562f72ada81081a12823d3c1590bedc48d7d2559410a2763fe/psycopg2_binary-2.9.11-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:04195548662fa544626c8ea0f06561eb6203f1984ba5b4562764fbeb4c3d14b1", size = 3347549, upload-time = "2025-10-10T11:13:03.971Z" },
    { url = "https://files.pythonhosted.org/packages/80/2d/1bb683f64737bbb1f86c82b7359db1eb2be4e2c0c13b947f80efefa7d3e5/psycopg2_binary-2.9.11-cp313-cp313-win_amd64.whl", hash = "sha256:efff12b432179443f54e230fdf60de1f6cc726b6c832db8701227d089310e8aa", size = 2714215, upload-time = "2025-10-10T11:13:07.14Z" },
    { url = "https://files.pythonhosted.org/packages/64/12/93ef0098590cf51d9732b4f139533732565704f45bdc1ffa741b7c95fb54/psycopg2_binary-2.9.11-cp314-cp314-macosx_10_13_x86_64.whl", hash = "sha256:92e3b669236327083a2e33ccfa0d320dd01b9803b3e14dd986a4fc54aa00f4e1", size = 3756567, upload-time = "2025-10-10T11:13:11.885Z" },
    { url = "https://files.pythonhosted.org/packages/7c/a9/9d55c614a891288f15ca4b5209b09f0f01e3124056924e17b81b9fa054cc/psycopg2_binary-2.9.11-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:e0deeb03da539fa3577fcb0b3f2554a97f7e5477c246098dbb18091a4a01c16f", size = 3864755, upload-time = "2025-10-10T11:13:17.727Z" },
    { url = "https://files.pythonhosted.org/packages/13/1e/98874ce72fd29cbde93209977b196a2edae03f8490d1bd8158e7f1daf3a0/psycopg2_binary-2.9.11-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:9b52a3f9bb540a3e4ec0f6ba6d31339727b2950c9772850d6545b7eae0b9d7c5", size = 4411646, upload-time = "2025-10-10T11:13:24.432Z" },
    { url = "https://files.pythonhosted.org/packages/5a/bd/a335ce6645334fb8d758cc358810defca14a1d19ffbc8a10bd38a2328565/psycopg2_binary-2.9.11-cp314-cp314-manylinux2014_ppc64le.manylinux_2_17_ppc64le.whl", hash = "sha256:db4fd476874ccfdbb630a54426964959e58da4c61c9feba73e6094d51303d7d8", size = 4468701, upload-time = "2025-10-10T11:13:29.266Z" },
    { url = "https://files.pythonhosted.org/packages/44/d6/c8b4f53f34e295e45709b7568bf9b9407a612ea30387d35eb9fa84f269b4/psycopg2_binary-2.9.11-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:47f212c1d3be608a12937cc131bd85502954398aaa1320cb4c14421a0ffccf4c", size = 4166293, upload-time = "2025-10-10T11:13:33.336Z" },
    { url = "https://files.pythonhosted.org/packages/4b/e0/f8cc36eadd1b716ab36bb290618a3292e009867e5c97ce4aba908cb99644/psycopg2_binary-2.9.11-cp314-cp314-manylinux_2_38_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:e35b7abae2b0adab776add56111df1735ccc71406e56203515e228a8dc07089f", size = 3983184, upload-time = "2025-10-30T02:55:32.483Z" },
    { url = "https://files.pythonhosted.org/packages/53/3e/2a8fe18a4e61cfb3417da67b6318e12691772c0696d79434184a511906dc/psycopg2_binary-2.9.11-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:fcf21be3ce5f5659daefd2b3b3b6e4727b028221ddc94e6c1523425579664747", size = 3652650, upload-time = "2025-10-10T11:13:38.181Z" },
    { url = "https://files.pythonhosted.org/packages/76/36/03801461b31b29fe58d228c24388f999fe814dfc302856e0d17f97d7c54d/psycopg2_binary-2.9.11-cp314-cp314-musllinux_1_2_ppc64le.whl", hash = "sha256:9bd81e64e8de111237737b29d68039b9c813bdf520156af36d26819c9a979e5f", size = 3298663, upload-time = "2025-10-10T11:13:44.878Z" },
    { url = "https://files.pythonhosted.org/packages/97/77/21b0ea2e1a73aa5fa9222b2a6b8ba325c43c3a8d54272839c991f2345656/psycopg2_binary-2.9.11-cp314-cp314-musllinux_1_2_riscv64.whl", hash = "sha256:32770a4d666fbdafab017086655bcddab791d7cb260a16679cc5a7338b64343b", size = 3044737, upload-time = "2025-10-30T02:55:35.69Z" },
    { url = "https://files.pythonhosted.org/packages/67/69/f36abe5f118c1dca6d3726ceae164b9356985805480731ac6712a63f24f0/psycopg2_binary-2.9.11-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:c3cb3a676873d7506825221045bd70e0427c905b9c8ee8d6acd70cfcbd6e576d", size = 3347643, upload-time = "2025-10-10T11:13:53.499Z" },
    { url = "https://files.pythonhosted.org/packages/e1/36/9c0c326fe3a4227953dfb29f5d0c8ae3b8eb8c1cd2967aa569f50cb3c61f/psycopg2_binary-2.9.11-cp314-cp314-win_amd64.whl", hash = "sha256:4012c9c954dfaccd28f94e84ab9f94e12df76b4afb22331b1f0d3154893a6316", size = 2803913, upload-time = "2025-10-10T11:13:57.058Z" },
]

[[package]]
name = "pyasn1"
version = "0.6.1"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/ba/e9/01f1a64245b89f039897cb0130016d79f77d52669aae6ee7b159a6c4c018/pyasn1-0.6.1.tar.gz", hash = "sha256:6f580d2bdd84365380830acf45550f2511469f673cb4a5ae3857a3170128b034", size = 145322, upload-time = "2024-09-10T22:41:42.55Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/c8/f1/d6a797abb14f6283c0ddff96bbdd46937f64122b8c925cab503dd37f8214/pyasn1-0.6.1-py3-none-any.whl", hash = "sha256:0d632f46f2ba09143da3a8afe9e33fb6f92fa2320ab7e886e2d0f7672af84629", size = 83135, upload-time = "2024-09-11T16:00:36.122Z" },
]

[[package]]
name = "pycodestyle"
version = "2.14.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/11/e0/abfd2a0d2efe47670df87f3e3a0e2edda42f055053c85361f19c0e2c1ca8/pycodestyle-2.14.0.tar.gz", hash = "sha256:c4b5b517d278089ff9d0abdec919cd97262a3367449ea1c8b49b91529167b783", size = 39472, upload-time = "2025-06-20T18:49:48.75Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/d7/27/a58ddaf8c588a3ef080db9d0b7e0b97215cee3a45df74f3a94dbbf5c893a/pycodestyle-2.14.0-py2.py3-none-any.whl", hash = "sha256:dd6bf7cb4ee77f8e016f9c8e74a35ddd9f67e1d5fd4184d86c3b98e07099f42d", size = 31594, upload-time = "2025-06-20T18:49:47.491Z" },
]

[[package]]
name = "pycparser"
version = "2.23"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/fe/cf/d2d3b9f5699fb1e4615c8e32ff220203e43b248e1dfcc6736ad9057731ca/pycparser-2.23.tar.gz", hash = "sha256:78816d4f24add8f10a06d6f05b4d424ad9e96cfebf68a4ddc99c65c0720d00c2", size = 173734, upload-time = "2025-09-09T13:23:47.91Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/a0/e3/59cd50310fc9b59512193629e1984c1f95e5c8ae6e5d8c69532ccc65a7fe/pycparser-2.23-py3-none-any.whl", hash = "sha256:e5c6e8d3fbad53479cab09ac03729e0a9faf2bee3db8208a550daf5af81a5934", size = 118140, upload-time = "2025-09-09T13:23:46.651Z" },
]

[[package]]
name = "pydyf"
version = "0.12.1"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/36/ee/fb410c5c854b6a081a49077912a9765aeffd8e07cbb0663cfda310b01fb4/pydyf-0.12.1.tar.gz", hash = "sha256:fbd7e759541ac725c29c506612003de393249b94310ea78ae44cb1d04b220095", size = 17716, upload-time = "2025-12-02T14:52:14.244Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/22/11/47efe2f66ba848a107adfd490b508f5c0cedc82127950553dca44d29e6c4/pydyf-0.12.1-py3-none-any.whl", hash = "sha256:ea25b4e1fe7911195cb57067560daaa266639184e8335365cc3ee5214e7eaadc", size = 8028, upload-time = "2025-12-02T14:52:12.938Z" },
]

[[package]]
name = "pyflakes"
version = "3.4.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/45/dc/fd034dc20b4b264b3d015808458391acbf9df40b1e54750ef175d39180b1/pyflakes-3.4.0.tar.gz", hash = "sha256:b24f96fafb7d2ab0ec5075b7350b3d2d2218eab42003821c06344973d3ea2f58", size = 64669, upload-time = "2025-06-20T18:45:27.834Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/c2/2f/81d580a0fb83baeb066698975cb14a618bdbed7720678566f1b046a95fe8/pyflakes-3.4.0-py2.py3-none-any.whl", hash = "sha256:f742a7dbd0d9cb9ea41e9a24a918996e8170c799fa528688d40dd582c8265f4f", size = 63551, upload-time = "2025-06-20T18:45:26.937Z" },
]

[[package]]
name = "pygments"
version = "2.19.2"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/b0/77/a5b8c569bf593b0140bde72ea885a803b82086995367bf2037de0159d924/pygments-2.19.2.tar.gz", hash = "sha256:636cb2477cec7f8952536970bc533bc43743542f70392ae026374600add5b887", size = 4968631, upload-time = "2025-06-21T13:39:12.283Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/c7/21/705964c7812476f378728bdf590ca4b771ec72385c533964653c68e86bdc/pygments-2.19.2-py3-none-any.whl", hash = "sha256:86540386c03d588bb81d44bc3928634ff26449851e99741617ecb9037ee5ec0b", size = 1225217, upload-time = "2025-06-21T13:39:07.939Z" },
]

[[package]]
name = "pyphen"
version = "0.17.2"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/69/56/e4d7e1bd70d997713649c5ce530b2d15a5fc2245a74ca820fc2d51d89d4d/pyphen-0.17.2.tar.gz", hash = "sha256:f60647a9c9b30ec6c59910097af82bc5dd2d36576b918e44148d8b07ef3b4aa3", size = 2079470, upload-time = "2025-01-20T13:18:36.296Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/7b/1f/c2142d2edf833a90728e5cdeb10bdbdc094dde8dbac078cee0cf33f5e11b/pyphen-0.17.2-py3-none-any.whl", hash = "sha256:3a07fb017cb2341e1d9ff31b8634efb1ae4dc4b130468c7c39dd3d32e7c3affd", size = 2079358, upload-time = "2025-01-20T13:18:29.629Z" },
]

[[package]]
name = "pytest"
version = "9.0.2"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "colorama", marker = "sys_platform == 'win32'" },
    { name = "iniconfig" },
    { name = "packaging" },
    { name = "pluggy" },
    { name = "pygments" },
]
sdist = { url = "https://files.pythonhosted.org/packages/d1/db/7ef3487e0fb0049ddb5ce41d3a49c235bf9ad299b6a25d5780a89f19230f/pytest-9.0.2.tar.gz", hash = "sha256:75186651a92bd89611d1d9fc20f0b4345fd827c41ccd5c299a868a05d70edf11", size = 1568901, upload-time = "2025-12-06T21:30:51.014Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/3b/ab/b3226f0bd7cdcf710fbede2b3548584366da3b19b5021e74f5bde2a8fa3f/pytest-9.0.2-py3-none-any.whl", hash = "sha256:711ffd45bf766d5264d487b917733b453d917afd2b0ad65223959f59089f875b", size = 374801, upload-time = "2025-12-06T21:30:49.154Z" },
]

[[package]]
name = "pytest-django"
version = "4.11.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "pytest" },
]
sdist = { url = "https://files.pythonhosted.org/packages/b1/fb/55d580352db26eb3d59ad50c64321ddfe228d3d8ac107db05387a2fadf3a/pytest_django-4.11.1.tar.gz", hash = "sha256:a949141a1ee103cb0e7a20f1451d355f83f5e4a5d07bdd4dcfdd1fd0ff227991", size = 86202, upload-time = "2025-04-03T18:56:09.338Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/be/ac/bd0608d229ec808e51a21044f3f2f27b9a37e7a0ebaca7247882e67876af/pytest_django-4.11.1-py3-none-any.whl", hash = "sha256:1b63773f648aa3d8541000c26929c1ea63934be1cfa674c76436966d73fe6a10", size = 25281, upload-time = "2025-04-03T18:56:07.678Z" },
]

[[package]]
name = "python-dateutil"
version = "2.9.0.post0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "six" },
]
sdist = { url = "https://files.pythonhosted.org/packages/66/c0/0c8b6ad9f17a802ee498c46e004a0eb49bc148f2fd230864601a86dcf6db/python-dateutil-2.9.0.post0.tar.gz", hash = "sha256:37dd54208da7e1cd875388217d5e00ebd4179249f90fb72437e91a35459a0ad3", size = 342432, upload-time = "2024-03-01T18:36:20.211Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/ec/57/56b9bcc3c9c6a792fcbaf139543cee77261f3651ca9da0c93f5c1221264b/python_dateutil-2.9.0.post0-py2.py3-none-any.whl", hash = "sha256:a8b2bc7bffae282281c8140a97d3aa9c14da0b136dfe83f850eea9a5f7470427", size = 229892, upload-time = "2024-03-01T18:36:18.57Z" },
]

[[package]]
name = "python-jose"
version = "3.5.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "ecdsa" },
    { name = "pyasn1" },
    { name = "rsa" },
]
sdist = { url = "https://files.pythonhosted.org/packages/c6/77/3a1c9039db7124eb039772b935f2244fbb73fc8ee65b9acf2375da1c07bf/python_jose-3.5.0.tar.gz", hash = "sha256:fb4eaa44dbeb1c26dcc69e4bd7ec54a1cb8dd64d3b4d81ef08d90ff453f2b01b", size = 92726, upload-time = "2025-05-28T17:31:54.288Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/d9/c3/0bd11992072e6a1c513b16500a5d07f91a24017c5909b02c72c62d7ad024/python_jose-3.5.0-py2.py3-none-any.whl", hash = "sha256:abd1202f23d34dfad2c3d28cb8617b90acf34132c7afd60abd0b0b7d3cb55771", size = 34624, upload-time = "2025-05-28T17:31:52.802Z" },
]

[[package]]
name = "pytokens"
version = "0.3.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/4e/8d/a762be14dae1c3bf280202ba3172020b2b0b4c537f94427435f19c413b72/pytokens-0.3.0.tar.gz", hash = "sha256:2f932b14ed08de5fcf0b391ace2642f858f1394c0857202959000b68ed7a458a", size = 17644, upload-time = "2025-11-05T13:36:35.34Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/84/25/d9db8be44e205a124f6c98bc0324b2bb149b7431c53877fc6d1038dddaf5/pytokens-0.3.0-py3-none-any.whl", hash = "sha256:95b2b5eaf832e469d141a378872480ede3f251a5a5041b8ec6e581d3ac71bbf3", size = 12195, upload-time = "2025-11-05T13:36:33.183Z" },
]

[[package]]
name = "pyyaml"
version = "6.0.3"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/05/8e/961c0007c59b8dd7729d542c61a4d537767a59645b82a0b521206e1e25c2/pyyaml-6.0.3.tar.gz", hash = "sha256:d76623373421df22fb4cf8817020cbb7ef15c725b9d5e45f17e189bfc384190f", size = 130960, upload-time = "2025-09-25T21:33:16.546Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/d1/33/422b98d2195232ca1826284a76852ad5a86fe23e31b009c9886b2d0fb8b2/pyyaml-6.0.3-cp312-cp312-macosx_10_13_x86_64.whl", hash = "sha256:7f047e29dcae44602496db43be01ad42fc6f1cc0d8cd6c83d342306c32270196", size = 182063, upload-time = "2025-09-25T21:32:11.445Z" },
    { url = "https://files.pythonhosted.org/packages/89/a0/6cf41a19a1f2f3feab0e9c0b74134aa2ce6849093d5517a0c550fe37a648/pyyaml-6.0.3-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:fc09d0aa354569bc501d4e787133afc08552722d3ab34836a80547331bb5d4a0", size = 173973, upload-time = "2025-09-25T21:32:12.492Z" },
    { url = "https://files.pythonhosted.org/packages/ed/23/7a778b6bd0b9a8039df8b1b1d80e2e2ad78aa04171592c8a5c43a56a6af4/pyyaml-6.0.3-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:9149cad251584d5fb4981be1ecde53a1ca46c891a79788c0df828d2f166bda28", size = 775116, upload-time = "2025-09-25T21:32:13.652Z" },
    { url = "https://files.pythonhosted.org/packages/65/30/d7353c338e12baef4ecc1b09e877c1970bd3382789c159b4f89d6a70dc09/pyyaml-6.0.3-cp312-cp312-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:5fdec68f91a0c6739b380c83b951e2c72ac0197ace422360e6d5a959d8d97b2c", size = 844011, upload-time = "2025-09-25T21:32:15.21Z" },
    { url = "https://files.pythonhosted.org/packages/8b/9d/b3589d3877982d4f2329302ef98a8026e7f4443c765c46cfecc8858c6b4b/pyyaml-6.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:ba1cc08a7ccde2d2ec775841541641e4548226580ab850948cbfda66a1befcdc", size = 807870, upload-time = "2025-09-25T21:32:16.431Z" },
    { url = "https://files.pythonhosted.org/packages/05/c0/b3be26a015601b822b97d9149ff8cb5ead58c66f981e04fedf4e762f4bd4/pyyaml-6.0.3-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:8dc52c23056b9ddd46818a57b78404882310fb473d63f17b07d5c40421e47f8e", size = 761089, upload-time = "2025-09-25T21:32:17.56Z" },
    { url = "https://files.pythonhosted.org/packages/be/8e/98435a21d1d4b46590d5459a22d88128103f8da4c2d4cb8f14f2a96504e1/pyyaml-6.0.3-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:41715c910c881bc081f1e8872880d3c650acf13dfa8214bad49ed4cede7c34ea", size = 790181, upload-time = "2025-09-25T21:32:18.834Z" },
    { url = "https://files.pythonhosted.org/packages/74/93/7baea19427dcfbe1e5a372d81473250b379f04b1bd3c4c5ff825e2327202/pyyaml-6.0.3-cp312-cp312-win32.whl", hash = "sha256:96b533f0e99f6579b3d4d4995707cf36df9100d67e0c8303a0c55b27b5f99bc5", size = 137658, upload-time = "2025-09-25T21:32:20.209Z" },
    { url = "https://files.pythonhosted.org/packages/86/bf/899e81e4cce32febab4fb42bb97dcdf66bc135272882d1987881a4b519e9/pyyaml-6.0.3-cp312-cp312-win_amd64.whl", hash = "sha256:5fcd34e47f6e0b794d17de1b4ff496c00986e1c83f7ab2fb8fcfe9616ff7477b", size = 154003, upload-time = "2025-09-25T21:32:21.167Z" },
    { url = "https://files.pythonhosted.org/packages/1a/08/67bd04656199bbb51dbed1439b7f27601dfb576fb864099c7ef0c3e55531/pyyaml-6.0.3-cp312-cp312-win_arm64.whl", hash = "sha256:64386e5e707d03a7e172c0701abfb7e10f0fb753ee1d773128192742712a98fd", size = 140344, upload-time = "2025-09-25T21:32:22.617Z" },
    { url = "https://files.pythonhosted.org/packages/d1/11/0fd08f8192109f7169db964b5707a2f1e8b745d4e239b784a5a1dd80d1db/pyyaml-6.0.3-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:8da9669d359f02c0b91ccc01cac4a67f16afec0dac22c2ad09f46bee0697eba8", size = 181669, upload-time = "2025-09-25T21:32:23.673Z" },
    { url = "https://files.pythonhosted.org/packages/b1/16/95309993f1d3748cd644e02e38b75d50cbc0d9561d21f390a76242ce073f/pyyaml-6.0.3-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:2283a07e2c21a2aa78d9c4442724ec1eb15f5e42a723b99cb3d822d48f5f7ad1", size = 173252, upload-time = "2025-09-25T21:32:25.149Z" },
    { url = "https://files.pythonhosted.org/packages/50/31/b20f376d3f810b9b2371e72ef5adb33879b25edb7a6d072cb7ca0c486398/pyyaml-6.0.3-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:ee2922902c45ae8ccada2c5b501ab86c36525b883eff4255313a253a3160861c", size = 767081, upload-time = "2025-09-25T21:32:26.575Z" },
    { url = "https://files.pythonhosted.org/packages/49/1e/a55ca81e949270d5d4432fbbd19dfea5321eda7c41a849d443dc92fd1ff7/pyyaml-6.0.3-cp313-cp313-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:a33284e20b78bd4a18c8c2282d549d10bc8408a2a7ff57653c0cf0b9be0afce5", size = 841159, upload-time = "2025-09-25T21:32:27.727Z" },
    { url = "https://files.pythonhosted.org/packages/74/27/e5b8f34d02d9995b80abcef563ea1f8b56d20134d8f4e5e81733b1feceb2/pyyaml-6.0.3-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:0f29edc409a6392443abf94b9cf89ce99889a1dd5376d94316ae5145dfedd5d6", size = 801626, upload-time = "2025-09-25T21:32:28.878Z" },
    { url = "https://files.pythonhosted.org/packages/f9/11/ba845c23988798f40e52ba45f34849aa8a1f2d4af4b798588010792ebad6/pyyaml-6.0.3-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:f7057c9a337546edc7973c0d3ba84ddcdf0daa14533c2065749c9075001090e6", size = 753613, upload-time = "2025-09-25T21:32:30.178Z" },
    { url = "https://files.pythonhosted.org/packages/3d/e0/7966e1a7bfc0a45bf0a7fb6b98ea03fc9b8d84fa7f2229e9659680b69ee3/pyyaml-6.0.3-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:eda16858a3cab07b80edaf74336ece1f986ba330fdb8ee0d6c0d68fe82bc96be", size = 794115, upload-time = "2025-09-25T21:32:31.353Z" },
    { url = "https://files.pythonhosted.org/packages/de/94/980b50a6531b3019e45ddeada0626d45fa85cbe22300844a7983285bed3b/pyyaml-6.0.3-cp313-cp313-win32.whl", hash = "sha256:d0eae10f8159e8fdad514efdc92d74fd8d682c933a6dd088030f3834bc8e6b26", size = 137427, upload-time = "2025-09-25T21:32:32.58Z" },
    { url = "https://files.pythonhosted.org/packages/97/c9/39d5b874e8b28845e4ec2202b5da735d0199dbe5b8fb85f91398814a9a46/pyyaml-6.0.3-cp313-cp313-win_amd64.whl", hash = "sha256:79005a0d97d5ddabfeeea4cf676af11e647e41d81c9a7722a193022accdb6b7c", size = 154090, upload-time = "2025-09-25T21:32:33.659Z" },
    { url = "https://files.pythonhosted.org/packages/73/e8/2bdf3ca2090f68bb3d75b44da7bbc71843b19c9f2b9cb9b0f4ab7a5a4329/pyyaml-6.0.3-cp313-cp313-win_arm64.whl", hash = "sha256:5498cd1645aa724a7c71c8f378eb29ebe23da2fc0d7a08071d89469bf1d2defb", size = 140246, upload-time = "2025-09-25T21:32:34.663Z" },
    { url = "https://files.pythonhosted.org/packages/9d/8c/f4bd7f6465179953d3ac9bc44ac1a8a3e6122cf8ada906b4f96c60172d43/pyyaml-6.0.3-cp314-cp314-macosx_10_13_x86_64.whl", hash = "sha256:8d1fab6bb153a416f9aeb4b8763bc0f22a5586065f86f7664fc23339fc1c1fac", size = 181814, upload-time = "2025-09-25T21:32:35.712Z" },
    { url = "https://files.pythonhosted.org/packages/bd/9c/4d95bb87eb2063d20db7b60faa3840c1b18025517ae857371c4dd55a6b3a/pyyaml-6.0.3-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:34d5fcd24b8445fadc33f9cf348c1047101756fd760b4dacb5c3e99755703310", size = 173809, upload-time = "2025-09-25T21:32:36.789Z" },
    { url = "https://files.pythonhosted.org/packages/92/b5/47e807c2623074914e29dabd16cbbdd4bf5e9b2db9f8090fa64411fc5382/pyyaml-6.0.3-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:501a031947e3a9025ed4405a168e6ef5ae3126c59f90ce0cd6f2bfc477be31b7", size = 766454, upload-time = "2025-09-25T21:32:37.966Z" },
    { url = "https://files.pythonhosted.org/packages/02/9e/e5e9b168be58564121efb3de6859c452fccde0ab093d8438905899a3a483/pyyaml-6.0.3-cp314-cp314-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:b3bc83488de33889877a0f2543ade9f70c67d66d9ebb4ac959502e12de895788", size = 836355, upload-time = "2025-09-25T21:32:39.178Z" },
    { url = "https://files.pythonhosted.org/packages/88/f9/16491d7ed2a919954993e48aa941b200f38040928474c9e85ea9e64222c3/pyyaml-6.0.3-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:c458b6d084f9b935061bc36216e8a69a7e293a2f1e68bf956dcd9e6cbcd143f5", size = 794175, upload-time = "2025-09-25T21:32:40.865Z" },
    { url = "https://files.pythonhosted.org/packages/dd/3f/5989debef34dc6397317802b527dbbafb2b4760878a53d4166579111411e/pyyaml-6.0.3-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:7c6610def4f163542a622a73fb39f534f8c101d690126992300bf3207eab9764", size = 755228, upload-time = "2025-09-25T21:32:42.084Z" },
    { url = "https://files.pythonhosted.org/packages/d7/ce/af88a49043cd2e265be63d083fc75b27b6ed062f5f9fd6cdc223ad62f03e/pyyaml-6.0.3-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:5190d403f121660ce8d1d2c1bb2ef1bd05b5f68533fc5c2ea899bd15f4399b35", size = 789194, upload-time = "2025-09-25T21:32:43.362Z" },
    { url = "https://files.pythonhosted.org/packages/23/20/bb6982b26a40bb43951265ba29d4c246ef0ff59c9fdcdf0ed04e0687de4d/pyyaml-6.0.3-cp314-cp314-win_amd64.whl", hash = "sha256:4a2e8cebe2ff6ab7d1050ecd59c25d4c8bd7e6f400f5f82b96557ac0abafd0ac", size = 156429, upload-time = "2025-09-25T21:32:57.844Z" },
    { url = "https://files.pythonhosted.org/packages/f4/f4/a4541072bb9422c8a883ab55255f918fa378ecf083f5b85e87fc2b4eda1b/pyyaml-6.0.3-cp314-cp314-win_arm64.whl", hash = "sha256:93dda82c9c22deb0a405ea4dc5f2d0cda384168e466364dec6255b293923b2f3", size = 143912, upload-time = "2025-09-25T21:32:59.247Z" },
    { url = "https://files.pythonhosted.org/packages/7c/f9/07dd09ae774e4616edf6cda684ee78f97777bdd15847253637a6f052a62f/pyyaml-6.0.3-cp314-cp314t-macosx_10_13_x86_64.whl", hash = "sha256:02893d100e99e03eda1c8fd5c441d8c60103fd175728e23e431db1b589cf5ab3", size = 189108, upload-time = "2025-09-25T21:32:44.377Z" },
    { url = "https://files.pythonhosted.org/packages/4e/78/8d08c9fb7ce09ad8c38ad533c1191cf27f7ae1effe5bb9400a46d9437fcf/pyyaml-6.0.3-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:c1ff362665ae507275af2853520967820d9124984e0f7466736aea23d8611fba", size = 183641, upload-time = "2025-09-25T21:32:45.407Z" },
    { url = "https://files.pythonhosted.org/packages/7b/5b/3babb19104a46945cf816d047db2788bcaf8c94527a805610b0289a01c6b/pyyaml-6.0.3-cp314-cp314t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:6adc77889b628398debc7b65c073bcb99c4a0237b248cacaf3fe8a557563ef6c", size = 831901, upload-time = "2025-09-25T21:32:48.83Z" },
    { url = "https://files.pythonhosted.org/packages/8b/cc/dff0684d8dc44da4d22a13f35f073d558c268780ce3c6ba1b87055bb0b87/pyyaml-6.0.3-cp314-cp314t-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:a80cb027f6b349846a3bf6d73b5e95e782175e52f22108cfa17876aaeff93702", size = 861132, upload-time = "2025-09-25T21:32:50.149Z" },
    { url = "https://files.pythonhosted.org/packages/b1/5e/f77dc6b9036943e285ba76b49e118d9ea929885becb0a29ba8a7c75e29fe/pyyaml-6.0.3-cp314-cp314t-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:00c4bdeba853cc34e7dd471f16b4114f4162dc03e6b7afcc2128711f0eca823c", size = 839261, upload-time = "2025-09-25T21:32:51.808Z" },
    { url = "https://files.pythonhosted.org/packages/ce/88/a9db1376aa2a228197c58b37302f284b5617f56a5d959fd1763fb1675ce6/pyyaml-6.0.3-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:66e1674c3ef6f541c35191caae2d429b967b99e02040f5ba928632d9a7f0f065", size = 805272, upload-time = "2025-09-25T21:32:52.941Z" },
    { url = "https://files.pythonhosted.org/packages/da/92/1446574745d74df0c92e6aa4a7b0b3130706a4142b2d1a5869f2eaa423c6/pyyaml-6.0.3-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:16249ee61e95f858e83976573de0f5b2893b3677ba71c9dd36b9cf8be9ac6d65", size = 829923, upload-time = "2025-09-25T21:32:54.537Z" },
    { url = "https://files.pythonhosted.org/packages/f0/7a/1c7270340330e575b92f397352af856a8c06f230aa3e76f86b39d01b416a/pyyaml-6.0.3-cp314-cp314t-win_amd64.whl", hash = "sha256:4ad1906908f2f5ae4e5a8ddfce73c320c2a1429ec52eafd27138b7f1cbe341c9", size = 174062, upload-time = "2025-09-25T21:32:55.767Z" },
    { url = "https://files.pythonhosted.org/packages/f1/12/de94a39c2ef588c7e6455cfbe7343d3b2dc9d6b6b2f40c4c6565744c873d/pyyaml-6.0.3-cp314-cp314t-win_arm64.whl", hash = "sha256:ebc55a14a21cb14062aa4162f906cd962b28e2e9ea38f9b4391244cd8de4ae0b", size = 149341, upload-time = "2025-09-25T21:32:56.828Z" },
]

[[package]]
name = "redis"
version = "7.1.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/43/c8/983d5c6579a411d8a99bc5823cc5712768859b5ce2c8afe1a65b37832c81/redis-7.1.0.tar.gz", hash = "sha256:b1cc3cfa5a2cb9c2ab3ba700864fb0ad75617b41f01352ce5779dabf6d5f9c3c", size = 4796669, upload-time = "2025-11-19T15:54:39.961Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/89/f0/8956f8a86b20d7bb9d6ac0187cf4cd54d8065bc9a1a09eb8011d4d326596/redis-7.1.0-py3-none-any.whl", hash = "sha256:23c52b208f92b56103e17c5d06bdc1a6c2c0b3106583985a76a18f83b265de2b", size = 354159, upload-time = "2025-11-19T15:54:38.064Z" },
]

[[package]]
name = "referencing"
version = "0.37.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "attrs" },
    { name = "rpds-py" },
    { name = "typing-extensions", marker = "python_full_version < '3.13'" },
]
sdist = { url = "https://files.pythonhosted.org/packages/22/f5/df4e9027acead3ecc63e50fe1e36aca1523e1719559c499951bb4b53188f/referencing-0.37.0.tar.gz", hash = "sha256:44aefc3142c5b842538163acb373e24cce6632bd54bdb01b21ad5863489f50d8", size = 78036, upload-time = "2025-10-13T15:30:48.871Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/2c/58/ca301544e1fa93ed4f80d724bf5b194f6e4b945841c5bfd555878eea9fcb/referencing-0.37.0-py3-none-any.whl", hash = "sha256:381329a9f99628c9069361716891d34ad94af76e461dcb0335825aecc7692231", size = 26766, upload-time = "2025-10-13T15:30:47.625Z" },
]

[[package]]
name = "requests"
version = "2.32.5"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "certifi" },
    { name = "charset-normalizer" },
    { name = "idna" },
    { name = "urllib3" },
]
sdist = { url = "https://files.pythonhosted.org/packages/c9/74/b3ff8e6c8446842c3f5c837e9c3dfcfe2018ea6ecef224c710c85ef728f4/requests-2.32.5.tar.gz", hash = "sha256:dbba0bac56e100853db0ea71b82b4dfd5fe2bf6d3754a8893c3af500cec7d7cf", size = 134517, upload-time = "2025-08-18T20:46:02.573Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/1e/db/4254e3eabe8020b458f1a747140d32277ec7a271daf1d235b70dc0b4e6e3/requests-2.32.5-py3-none-any.whl", hash = "sha256:2462f94637a34fd532264295e186976db0f5d453d1cdd31473c85a6a161affb6", size = 64738, upload-time = "2025-08-18T20:46:00.542Z" },
]

[[package]]
name = "rpds-py"
version = "0.30.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/20/af/3f2f423103f1113b36230496629986e0ef7e199d2aa8392452b484b38ced/rpds_py-0.30.0.tar.gz", hash = "sha256:dd8ff7cf90014af0c0f787eea34794ebf6415242ee1d6fa91eaba725cc441e84", size = 69469, upload-time = "2025-11-30T20:24:38.837Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/03/e7/98a2f4ac921d82f33e03f3835f5bf3a4a40aa1bfdc57975e74a97b2b4bdd/rpds_py-0.30.0-cp312-cp312-macosx_10_12_x86_64.whl", hash = "sha256:a161f20d9a43006833cd7068375a94d035714d73a172b681d8881820600abfad", size = 375086, upload-time = "2025-11-30T20:22:17.93Z" },
    { url = "https://files.pythonhosted.org/packages/4d/a1/bca7fd3d452b272e13335db8d6b0b3ecde0f90ad6f16f3328c6fb150c889/rpds_py-0.30.0-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:6abc8880d9d036ecaafe709079969f56e876fcf107f7a8e9920ba6d5a3878d05", size = 359053, upload-time = "2025-11-30T20:22:19.297Z" },
    { url = "https://files.pythonhosted.org/packages/65/1c/ae157e83a6357eceff62ba7e52113e3ec4834a84cfe07fa4b0757a7d105f/rpds_py-0.30.0-cp312-cp312-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:ca28829ae5f5d569bb62a79512c842a03a12576375d5ece7d2cadf8abe96ec28", size = 390763, upload-time = "2025-11-30T20:22:21.661Z" },
    { url = "https://files.pythonhosted.org/packages/d4/36/eb2eb8515e2ad24c0bd43c3ee9cd74c33f7ca6430755ccdb240fd3144c44/rpds_py-0.30.0-cp312-cp312-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:a1010ed9524c73b94d15919ca4d41d8780980e1765babf85f9a2f90d247153dd", size = 408951, upload-time = "2025-11-30T20:22:23.408Z" },
    { url = "https://files.pythonhosted.org/packages/d6/65/ad8dc1784a331fabbd740ef6f71ce2198c7ed0890dab595adb9ea2d775a1/rpds_py-0.30.0-cp312-cp312-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:f8d1736cfb49381ba528cd5baa46f82fdc65c06e843dab24dd70b63d09121b3f", size = 514622, upload-time = "2025-11-30T20:22:25.16Z" },
    { url = "https://files.pythonhosted.org/packages/63/8e/0cfa7ae158e15e143fe03993b5bcd743a59f541f5952e1546b1ac1b5fd45/rpds_py-0.30.0-cp312-cp312-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:d948b135c4693daff7bc2dcfc4ec57237a29bd37e60c2fabf5aff2bbacf3e2f1", size = 414492, upload-time = "2025-11-30T20:22:26.505Z" },
    { url = "https://files.pythonhosted.org/packages/60/1b/6f8f29f3f995c7ffdde46a626ddccd7c63aefc0efae881dc13b6e5d5bb16/rpds_py-0.30.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:47f236970bccb2233267d89173d3ad2703cd36a0e2a6e92d0560d333871a3d23", size = 394080, upload-time = "2025-11-30T20:22:27.934Z" },
    { url = "https://files.pythonhosted.org/packages/6d/d5/a266341051a7a3ca2f4b750a3aa4abc986378431fc2da508c5034d081b70/rpds_py-0.30.0-cp312-cp312-manylinux_2_31_riscv64.whl", hash = "sha256:2e6ecb5a5bcacf59c3f912155044479af1d0b6681280048b338b28e364aca1f6", size = 408680, upload-time = "2025-11-30T20:22:29.341Z" },
    { url = "https://files.pythonhosted.org/packages/10/3b/71b725851df9ab7a7a4e33cf36d241933da66040d195a84781f49c50490c/rpds_py-0.30.0-cp312-cp312-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:a8fa71a2e078c527c3e9dc9fc5a98c9db40bcc8a92b4e8858e36d329f8684b51", size = 423589, upload-time = "2025-11-30T20:22:31.469Z" },
    { url = "https://files.pythonhosted.org/packages/00/2b/e59e58c544dc9bd8bd8384ecdb8ea91f6727f0e37a7131baeff8d6f51661/rpds_py-0.30.0-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:73c67f2db7bc334e518d097c6d1e6fed021bbc9b7d678d6cc433478365d1d5f5", size = 573289, upload-time = "2025-11-30T20:22:32.997Z" },
    { url = "https://files.pythonhosted.org/packages/da/3e/a18e6f5b460893172a7d6a680e86d3b6bc87a54c1f0b03446a3c8c7b588f/rpds_py-0.30.0-cp312-cp312-musllinux_1_2_i686.whl", hash = "sha256:5ba103fb455be00f3b1c2076c9d4264bfcb037c976167a6047ed82f23153f02e", size = 599737, upload-time = "2025-11-30T20:22:34.419Z" },
    { url = "https://files.pythonhosted.org/packages/5c/e2/714694e4b87b85a18e2c243614974413c60aa107fd815b8cbc42b873d1d7/rpds_py-0.30.0-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:7cee9c752c0364588353e627da8a7e808a66873672bcb5f52890c33fd965b394", size = 563120, upload-time = "2025-11-30T20:22:35.903Z" },
    { url = "https://files.pythonhosted.org/packages/6f/ab/d5d5e3bcedb0a77f4f613706b750e50a5a3ba1c15ccd3665ecc636c968fd/rpds_py-0.30.0-cp312-cp312-win32.whl", hash = "sha256:1ab5b83dbcf55acc8b08fc62b796ef672c457b17dbd7820a11d6c52c06839bdf", size = 223782, upload-time = "2025-11-30T20:22:37.271Z" },
    { url = "https://files.pythonhosted.org/packages/39/3b/f786af9957306fdc38a74cef405b7b93180f481fb48453a114bb6465744a/rpds_py-0.30.0-cp312-cp312-win_amd64.whl", hash = "sha256:a090322ca841abd453d43456ac34db46e8b05fd9b3b4ac0c78bcde8b089f959b", size = 240463, upload-time = "2025-11-30T20:22:39.021Z" },
    { url = "https://files.pythonhosted.org/packages/f3/d2/b91dc748126c1559042cfe41990deb92c4ee3e2b415f6b5234969ffaf0cc/rpds_py-0.30.0-cp312-cp312-win_arm64.whl", hash = "sha256:669b1805bd639dd2989b281be2cfd951c6121b65e729d9b843e9639ef1fd555e", size = 230868, upload-time = "2025-11-30T20:22:40.493Z" },
    { url = "https://files.pythonhosted.org/packages/ed/dc/d61221eb88ff410de3c49143407f6f3147acf2538c86f2ab7ce65ae7d5f9/rpds_py-0.30.0-cp313-cp313-macosx_10_12_x86_64.whl", hash = "sha256:f83424d738204d9770830d35290ff3273fbb02b41f919870479fab14b9d303b2", size = 374887, upload-time = "2025-11-30T20:22:41.812Z" },
    { url = "https://files.pythonhosted.org/packages/fd/32/55fb50ae104061dbc564ef15cc43c013dc4a9f4527a1f4d99baddf56fe5f/rpds_py-0.30.0-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:e7536cd91353c5273434b4e003cbda89034d67e7710eab8761fd918ec6c69cf8", size = 358904, upload-time = "2025-11-30T20:22:43.479Z" },
    { url = "https://files.pythonhosted.org/packages/58/70/faed8186300e3b9bdd138d0273109784eea2396c68458ed580f885dfe7ad/rpds_py-0.30.0-cp313-cp313-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:2771c6c15973347f50fece41fc447c054b7ac2ae0502388ce3b6738cd366e3d4", size = 389945, upload-time = "2025-11-30T20:22:44.819Z" },
    { url = "https://files.pythonhosted.org/packages/bd/a8/073cac3ed2c6387df38f71296d002ab43496a96b92c823e76f46b8af0543/rpds_py-0.30.0-cp313-cp313-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:0a59119fc6e3f460315fe9d08149f8102aa322299deaa5cab5b40092345c2136", size = 407783, upload-time = "2025-11-30T20:22:46.103Z" },
    { url = "https://files.pythonhosted.org/packages/77/57/5999eb8c58671f1c11eba084115e77a8899d6e694d2a18f69f0ba471ec8b/rpds_py-0.30.0-cp313-cp313-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:76fec018282b4ead0364022e3c54b60bf368b9d926877957a8624b58419169b7", size = 515021, upload-time = "2025-11-30T20:22:47.458Z" },
    { url = "https://files.pythonhosted.org/packages/e0/af/5ab4833eadc36c0a8ed2bc5c0de0493c04f6c06de223170bd0798ff98ced/rpds_py-0.30.0-cp313-cp313-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:692bef75a5525db97318e8cd061542b5a79812d711ea03dbc1f6f8dbb0c5f0d2", size = 414589, upload-time = "2025-11-30T20:22:48.872Z" },
    { url = "https://files.pythonhosted.org/packages/b7/de/f7192e12b21b9e9a68a6d0f249b4af3fdcdff8418be0767a627564afa1f1/rpds_py-0.30.0-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:9027da1ce107104c50c81383cae773ef5c24d296dd11c99e2629dbd7967a20c6", size = 394025, upload-time = "2025-11-30T20:22:50.196Z" },
    { url = "https://files.pythonhosted.org/packages/91/c4/fc70cd0249496493500e7cc2de87504f5aa6509de1e88623431fec76d4b6/rpds_py-0.30.0-cp313-cp313-manylinux_2_31_riscv64.whl", hash = "sha256:9cf69cdda1f5968a30a359aba2f7f9aa648a9ce4b580d6826437f2b291cfc86e", size = 408895, upload-time = "2025-11-30T20:22:51.87Z" },
    { url = "https://files.pythonhosted.org/packages/58/95/d9275b05ab96556fefff73a385813eb66032e4c99f411d0795372d9abcea/rpds_py-0.30.0-cp313-cp313-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:a4796a717bf12b9da9d3ad002519a86063dcac8988b030e405704ef7d74d2d9d", size = 422799, upload-time = "2025-11-30T20:22:53.341Z" },
    { url = "https://files.pythonhosted.org/packages/06/c1/3088fc04b6624eb12a57eb814f0d4997a44b0d208d6cace713033ff1a6ba/rpds_py-0.30.0-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:5d4c2aa7c50ad4728a094ebd5eb46c452e9cb7edbfdb18f9e1221f597a73e1e7", size = 572731, upload-time = "2025-11-30T20:22:54.778Z" },
    { url = "https://files.pythonhosted.org/packages/d8/42/c612a833183b39774e8ac8fecae81263a68b9583ee343db33ab571a7ce55/rpds_py-0.30.0-cp313-cp313-musllinux_1_2_i686.whl", hash = "sha256:ba81a9203d07805435eb06f536d95a266c21e5b2dfbf6517748ca40c98d19e31", size = 599027, upload-time = "2025-11-30T20:22:56.212Z" },
    { url = "https://files.pythonhosted.org/packages/5f/60/525a50f45b01d70005403ae0e25f43c0384369ad24ffe46e8d9068b50086/rpds_py-0.30.0-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:945dccface01af02675628334f7cf49c2af4c1c904748efc5cf7bbdf0b579f95", size = 563020, upload-time = "2025-11-30T20:22:58.2Z" },
    { url = "https://files.pythonhosted.org/packages/0b/5d/47c4655e9bcd5ca907148535c10e7d489044243cc9941c16ed7cd53be91d/rpds_py-0.30.0-cp313-cp313-win32.whl", hash = "sha256:b40fb160a2db369a194cb27943582b38f79fc4887291417685f3ad693c5a1d5d", size = 223139, upload-time = "2025-11-30T20:23:00.209Z" },
    { url = "https://files.pythonhosted.org/packages/f2/e1/485132437d20aa4d3e1d8b3fb5a5e65aa8139f1e097080c2a8443201742c/rpds_py-0.30.0-cp313-cp313-win_amd64.whl", hash = "sha256:806f36b1b605e2d6a72716f321f20036b9489d29c51c91f4dd29a3e3afb73b15", size = 240224, upload-time = "2025-11-30T20:23:02.008Z" },
    { url = "https://files.pythonhosted.org/packages/24/95/ffd128ed1146a153d928617b0ef673960130be0009c77d8fbf0abe306713/rpds_py-0.30.0-cp313-cp313-win_arm64.whl", hash = "sha256:d96c2086587c7c30d44f31f42eae4eac89b60dabbac18c7669be3700f13c3ce1", size = 230645, upload-time = "2025-11-30T20:23:03.43Z" },
    { url = "https://files.pythonhosted.org/packages/ff/1b/b10de890a0def2a319a2626334a7f0ae388215eb60914dbac8a3bae54435/rpds_py-0.30.0-cp313-cp313t-macosx_10_12_x86_64.whl", hash = "sha256:eb0b93f2e5c2189ee831ee43f156ed34e2a89a78a66b98cadad955972548be5a", size = 364443, upload-time = "2025-11-30T20:23:04.878Z" },
    { url = "https://files.pythonhosted.org/packages/0d/bf/27e39f5971dc4f305a4fb9c672ca06f290f7c4e261c568f3dea16a410d47/rpds_py-0.30.0-cp313-cp313t-macosx_11_0_arm64.whl", hash = "sha256:922e10f31f303c7c920da8981051ff6d8c1a56207dbdf330d9047f6d30b70e5e", size = 353375, upload-time = "2025-11-30T20:23:06.342Z" },
    { url = "https://files.pythonhosted.org/packages/40/58/442ada3bba6e8e6615fc00483135c14a7538d2ffac30e2d933ccf6852232/rpds_py-0.30.0-cp313-cp313t-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:cdc62c8286ba9bf7f47befdcea13ea0e26bf294bda99758fd90535cbaf408000", size = 383850, upload-time = "2025-11-30T20:23:07.825Z" },
    { url = "https://files.pythonhosted.org/packages/14/14/f59b0127409a33c6ef6f5c1ebd5ad8e32d7861c9c7adfa9a624fc3889f6c/rpds_py-0.30.0-cp313-cp313t-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:47f9a91efc418b54fb8190a6b4aa7813a23fb79c51f4bb84e418f5476c38b8db", size = 392812, upload-time = "2025-11-30T20:23:09.228Z" },
    { url = "https://files.pythonhosted.org/packages/b3/66/e0be3e162ac299b3a22527e8913767d869e6cc75c46bd844aa43fb81ab62/rpds_py-0.30.0-cp313-cp313t-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:1f3587eb9b17f3789ad50824084fa6f81921bbf9a795826570bda82cb3ed91f2", size = 517841, upload-time = "2025-11-30T20:23:11.186Z" },
    { url = "https://files.pythonhosted.org/packages/3d/55/fa3b9cf31d0c963ecf1ba777f7cf4b2a2c976795ac430d24a1f43d25a6ba/rpds_py-0.30.0-cp313-cp313t-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:39c02563fc592411c2c61d26b6c5fe1e51eaa44a75aa2c8735ca88b0d9599daa", size = 408149, upload-time = "2025-11-30T20:23:12.864Z" },
    { url = "https://files.pythonhosted.org/packages/60/ca/780cf3b1a32b18c0f05c441958d3758f02544f1d613abf9488cd78876378/rpds_py-0.30.0-cp313-cp313t-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:51a1234d8febafdfd33a42d97da7a43f5dcb120c1060e352a3fbc0c6d36e2083", size = 383843, upload-time = "2025-11-30T20:23:14.638Z" },
    { url = "https://files.pythonhosted.org/packages/82/86/d5f2e04f2aa6247c613da0c1dd87fcd08fa17107e858193566048a1e2f0a/rpds_py-0.30.0-cp313-cp313t-manylinux_2_31_riscv64.whl", hash = "sha256:eb2c4071ab598733724c08221091e8d80e89064cd472819285a9ab0f24bcedb9", size = 396507, upload-time = "2025-11-30T20:23:16.105Z" },
    { url = "https://files.pythonhosted.org/packages/4b/9a/453255d2f769fe44e07ea9785c8347edaf867f7026872e76c1ad9f7bed92/rpds_py-0.30.0-cp313-cp313t-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:6bdfdb946967d816e6adf9a3d8201bfad269c67efe6cefd7093ef959683c8de0", size = 414949, upload-time = "2025-11-30T20:23:17.539Z" },
    { url = "https://files.pythonhosted.org/packages/a3/31/622a86cdc0c45d6df0e9ccb6becdba5074735e7033c20e401a6d9d0e2ca0/rpds_py-0.30.0-cp313-cp313t-musllinux_1_2_aarch64.whl", hash = "sha256:c77afbd5f5250bf27bf516c7c4a016813eb2d3e116139aed0096940c5982da94", size = 565790, upload-time = "2025-11-30T20:23:19.029Z" },
    { url = "https://files.pythonhosted.org/packages/1c/5d/15bbf0fb4a3f58a3b1c67855ec1efcc4ceaef4e86644665fff03e1b66d8d/rpds_py-0.30.0-cp313-cp313t-musllinux_1_2_i686.whl", hash = "sha256:61046904275472a76c8c90c9ccee9013d70a6d0f73eecefd38c1ae7c39045a08", size = 590217, upload-time = "2025-11-30T20:23:20.885Z" },
    { url = "https://files.pythonhosted.org/packages/6d/61/21b8c41f68e60c8cc3b2e25644f0e3681926020f11d06ab0b78e3c6bbff1/rpds_py-0.30.0-cp313-cp313t-musllinux_1_2_x86_64.whl", hash = "sha256:4c5f36a861bc4b7da6516dbdf302c55313afa09b81931e8280361a4f6c9a2d27", size = 555806, upload-time = "2025-11-30T20:23:22.488Z" },
    { url = "https://files.pythonhosted.org/packages/f9/39/7e067bb06c31de48de3eb200f9fc7c58982a4d3db44b07e73963e10d3be9/rpds_py-0.30.0-cp313-cp313t-win32.whl", hash = "sha256:3d4a69de7a3e50ffc214ae16d79d8fbb0922972da0356dcf4d0fdca2878559c6", size = 211341, upload-time = "2025-11-30T20:23:24.449Z" },
    { url = "https://files.pythonhosted.org/packages/0a/4d/222ef0b46443cf4cf46764d9c630f3fe4abaa7245be9417e56e9f52b8f65/rpds_py-0.30.0-cp313-cp313t-win_amd64.whl", hash = "sha256:f14fc5df50a716f7ece6a80b6c78bb35ea2ca47c499e422aa4463455dd96d56d", size = 225768, upload-time = "2025-11-30T20:23:25.908Z" },
    { url = "https://files.pythonhosted.org/packages/86/81/dad16382ebbd3d0e0328776d8fd7ca94220e4fa0798d1dc5e7da48cb3201/rpds_py-0.30.0-cp314-cp314-macosx_10_12_x86_64.whl", hash = "sha256:68f19c879420aa08f61203801423f6cd5ac5f0ac4ac82a2368a9fcd6a9a075e0", size = 362099, upload-time = "2025-11-30T20:23:27.316Z" },
    { url = "https://files.pythonhosted.org/packages/2b/60/19f7884db5d5603edf3c6bce35408f45ad3e97e10007df0e17dd57af18f8/rpds_py-0.30.0-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:ec7c4490c672c1a0389d319b3a9cfcd098dcdc4783991553c332a15acf7249be", size = 353192, upload-time = "2025-11-30T20:23:29.151Z" },
    { url = "https://files.pythonhosted.org/packages/bf/c4/76eb0e1e72d1a9c4703c69607cec123c29028bff28ce41588792417098ac/rpds_py-0.30.0-cp314-cp314-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:f251c812357a3fed308d684a5079ddfb9d933860fc6de89f2b7ab00da481e65f", size = 384080, upload-time = "2025-11-30T20:23:30.785Z" },
    { url = "https://files.pythonhosted.org/packages/72/87/87ea665e92f3298d1b26d78814721dc39ed8d2c74b86e83348d6b48a6f31/rpds_py-0.30.0-cp314-cp314-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:ac98b175585ecf4c0348fd7b29c3864bda53b805c773cbf7bfdaffc8070c976f", size = 394841, upload-time = "2025-11-30T20:23:32.209Z" },
    { url = "https://files.pythonhosted.org/packages/77/ad/7783a89ca0587c15dcbf139b4a8364a872a25f861bdb88ed99f9b0dec985/rpds_py-0.30.0-cp314-cp314-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:3e62880792319dbeb7eb866547f2e35973289e7d5696c6e295476448f5b63c87", size = 516670, upload-time = "2025-11-30T20:23:33.742Z" },
    { url = "https://files.pythonhosted.org/packages/5b/3c/2882bdac942bd2172f3da574eab16f309ae10a3925644e969536553cb4ee/rpds_py-0.30.0-cp314-cp314-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:4e7fc54e0900ab35d041b0601431b0a0eb495f0851a0639b6ef90f7741b39a18", size = 408005, upload-time = "2025-11-30T20:23:35.253Z" },
    { url = "https://files.pythonhosted.org/packages/ce/81/9a91c0111ce1758c92516a3e44776920b579d9a7c09b2b06b642d4de3f0f/rpds_py-0.30.0-cp314-cp314-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:47e77dc9822d3ad616c3d5759ea5631a75e5809d5a28707744ef79d7a1bcfcad", size = 382112, upload-time = "2025-11-30T20:23:36.842Z" },
    { url = "https://files.pythonhosted.org/packages/cf/8e/1da49d4a107027e5fbc64daeab96a0706361a2918da10cb41769244b805d/rpds_py-0.30.0-cp314-cp314-manylinux_2_31_riscv64.whl", hash = "sha256:b4dc1a6ff022ff85ecafef7979a2c6eb423430e05f1165d6688234e62ba99a07", size = 399049, upload-time = "2025-11-30T20:23:38.343Z" },
    { url = "https://files.pythonhosted.org/packages/df/5a/7ee239b1aa48a127570ec03becbb29c9d5a9eb092febbd1699d567cae859/rpds_py-0.30.0-cp314-cp314-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:4559c972db3a360808309e06a74628b95eaccbf961c335c8fe0d590cf587456f", size = 415661, upload-time = "2025-11-30T20:23:40.263Z" },
    { url = "https://files.pythonhosted.org/packages/70/ea/caa143cf6b772f823bc7929a45da1fa83569ee49b11d18d0ada7f5ee6fd6/rpds_py-0.30.0-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:0ed177ed9bded28f8deb6ab40c183cd1192aa0de40c12f38be4d59cd33cb5c65", size = 565606, upload-time = "2025-11-30T20:23:42.186Z" },
    { url = "https://files.pythonhosted.org/packages/64/91/ac20ba2d69303f961ad8cf55bf7dbdb4763f627291ba3d0d7d67333cced9/rpds_py-0.30.0-cp314-cp314-musllinux_1_2_i686.whl", hash = "sha256:ad1fa8db769b76ea911cb4e10f049d80bf518c104f15b3edb2371cc65375c46f", size = 591126, upload-time = "2025-11-30T20:23:44.086Z" },
    { url = "https://files.pythonhosted.org/packages/21/20/7ff5f3c8b00c8a95f75985128c26ba44503fb35b8e0259d812766ea966c7/rpds_py-0.30.0-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:46e83c697b1f1c72b50e5ee5adb4353eef7406fb3f2043d64c33f20ad1c2fc53", size = 553371, upload-time = "2025-11-30T20:23:46.004Z" },
    { url = "https://files.pythonhosted.org/packages/72/c7/81dadd7b27c8ee391c132a6b192111ca58d866577ce2d9b0ca157552cce0/rpds_py-0.30.0-cp314-cp314-win32.whl", hash = "sha256:ee454b2a007d57363c2dfd5b6ca4a5d7e2c518938f8ed3b706e37e5d470801ed", size = 215298, upload-time = "2025-11-30T20:23:47.696Z" },
    { url = "https://files.pythonhosted.org/packages/3e/d2/1aaac33287e8cfb07aab2e6b8ac1deca62f6f65411344f1433c55e6f3eb8/rpds_py-0.30.0-cp314-cp314-win_amd64.whl", hash = "sha256:95f0802447ac2d10bcc69f6dc28fe95fdf17940367b21d34e34c737870758950", size = 228604, upload-time = "2025-11-30T20:23:49.501Z" },
    { url = "https://files.pythonhosted.org/packages/e8/95/ab005315818cc519ad074cb7784dae60d939163108bd2b394e60dc7b5461/rpds_py-0.30.0-cp314-cp314-win_arm64.whl", hash = "sha256:613aa4771c99f03346e54c3f038e4cc574ac09a3ddfb0e8878487335e96dead6", size = 222391, upload-time = "2025-11-30T20:23:50.96Z" },
    { url = "https://files.pythonhosted.org/packages/9e/68/154fe0194d83b973cdedcdcc88947a2752411165930182ae41d983dcefa6/rpds_py-0.30.0-cp314-cp314t-macosx_10_12_x86_64.whl", hash = "sha256:7e6ecfcb62edfd632e56983964e6884851786443739dbfe3582947e87274f7cb", size = 364868, upload-time = "2025-11-30T20:23:52.494Z" },
    { url = "https://files.pythonhosted.org/packages/83/69/8bbc8b07ec854d92a8b75668c24d2abcb1719ebf890f5604c61c9369a16f/rpds_py-0.30.0-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:a1d0bc22a7cdc173fedebb73ef81e07faef93692b8c1ad3733b67e31e1b6e1b8", size = 353747, upload-time = "2025-11-30T20:23:54.036Z" },
    { url = "https://files.pythonhosted.org/packages/ab/00/ba2e50183dbd9abcce9497fa5149c62b4ff3e22d338a30d690f9af970561/rpds_py-0.30.0-cp314-cp314t-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:0d08f00679177226c4cb8c5265012eea897c8ca3b93f429e546600c971bcbae7", size = 383795, upload-time = "2025-11-30T20:23:55.556Z" },
    { url = "https://files.pythonhosted.org/packages/05/6f/86f0272b84926bcb0e4c972262f54223e8ecc556b3224d281e6598fc9268/rpds_py-0.30.0-cp314-cp314t-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:5965af57d5848192c13534f90f9dd16464f3c37aaf166cc1da1cae1fd5a34898", size = 393330, upload-time = "2025-11-30T20:23:57.033Z" },
    { url = "https://files.pythonhosted.org/packages/cb/e9/0e02bb2e6dc63d212641da45df2b0bf29699d01715913e0d0f017ee29438/rpds_py-0.30.0-cp314-cp314t-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:9a4e86e34e9ab6b667c27f3211ca48f73dba7cd3d90f8d5b11be56e5dbc3fb4e", size = 518194, upload-time = "2025-11-30T20:23:58.637Z" },
    { url = "https://files.pythonhosted.org/packages/ee/ca/be7bca14cf21513bdf9c0606aba17d1f389ea2b6987035eb4f62bd923f25/rpds_py-0.30.0-cp314-cp314t-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:e5d3e6b26f2c785d65cc25ef1e5267ccbe1b069c5c21b8cc724efee290554419", size = 408340, upload-time = "2025-11-30T20:24:00.2Z" },
    { url = "https://files.pythonhosted.org/packages/c2/c7/736e00ebf39ed81d75544c0da6ef7b0998f8201b369acf842f9a90dc8fce/rpds_py-0.30.0-cp314-cp314t-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:626a7433c34566535b6e56a1b39a7b17ba961e97ce3b80ec62e6f1312c025551", size = 383765, upload-time = "2025-11-30T20:24:01.759Z" },
    { url = "https://files.pythonhosted.org/packages/4a/3f/da50dfde9956aaf365c4adc9533b100008ed31aea635f2b8d7b627e25b49/rpds_py-0.30.0-cp314-cp314t-manylinux_2_31_riscv64.whl", hash = "sha256:acd7eb3f4471577b9b5a41baf02a978e8bdeb08b4b355273994f8b87032000a8", size = 396834, upload-time = "2025-11-30T20:24:03.687Z" },
    { url = "https://files.pythonhosted.org/packages/4e/00/34bcc2565b6020eab2623349efbdec810676ad571995911f1abdae62a3a0/rpds_py-0.30.0-cp314-cp314t-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:fe5fa731a1fa8a0a56b0977413f8cacac1768dad38d16b3a296712709476fbd5", size = 415470, upload-time = "2025-11-30T20:24:05.232Z" },
    { url = "https://files.pythonhosted.org/packages/8c/28/882e72b5b3e6f718d5453bd4d0d9cf8df36fddeb4ddbbab17869d5868616/rpds_py-0.30.0-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:74a3243a411126362712ee1524dfc90c650a503502f135d54d1b352bd01f2404", size = 565630, upload-time = "2025-11-30T20:24:06.878Z" },
    { url = "https://files.pythonhosted.org/packages/3b/97/04a65539c17692de5b85c6e293520fd01317fd878ea1995f0367d4532fb1/rpds_py-0.30.0-cp314-cp314t-musllinux_1_2_i686.whl", hash = "sha256:3e8eeb0544f2eb0d2581774be4c3410356eba189529a6b3e36bbbf9696175856", size = 591148, upload-time = "2025-11-30T20:24:08.445Z" },
    { url = "https://files.pythonhosted.org/packages/85/70/92482ccffb96f5441aab93e26c4d66489eb599efdcf96fad90c14bbfb976/rpds_py-0.30.0-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:dbd936cde57abfee19ab3213cf9c26be06d60750e60a8e4dd85d1ab12c8b1f40", size = 556030, upload-time = "2025-11-30T20:24:10.956Z" },
    { url = "https://files.pythonhosted.org/packages/20/53/7c7e784abfa500a2b6b583b147ee4bb5a2b3747a9166bab52fec4b5b5e7d/rpds_py-0.30.0-cp314-cp314t-win32.whl", hash = "sha256:dc824125c72246d924f7f796b4f63c1e9dc810c7d9e2355864b3c3a73d59ade0", size = 211570, upload-time = "2025-11-30T20:24:12.735Z" },
    { url = "https://files.pythonhosted.org/packages/d0/02/fa464cdfbe6b26e0600b62c528b72d8608f5cc49f96b8d6e38c95d60c676/rpds_py-0.30.0-cp314-cp314t-win_amd64.whl", hash = "sha256:27f4b0e92de5bfbc6f86e43959e6edd1425c33b5e69aab0984a72047f2bcf1e3", size = 226532, upload-time = "2025-11-30T20:24:14.634Z" },
]

[[package]]
name = "rsa"
version = "4.9.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "pyasn1" },
]
sdist = { url = "https://files.pythonhosted.org/packages/da/8a/22b7beea3ee0d44b1916c0c1cb0ee3af23b700b6da9f04991899d0c555d4/rsa-4.9.1.tar.gz", hash = "sha256:e7bdbfdb5497da4c07dfd35530e1a902659db6ff241e39d9953cad06ebd0ae75", size = 29034, upload-time = "2025-04-16T09:51:18.218Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/64/8d/0133e4eb4beed9e425d9a98ed6e081a55d195481b7632472be1af08d2f6b/rsa-4.9.1-py3-none-any.whl", hash = "sha256:68635866661c6836b8d39430f97a996acbd61bfa49406748ea243539fe239762", size = 34696, upload-time = "2025-04-16T09:51:17.142Z" },
]

[[package]]
name = "sentry-sdk"
version = "2.48.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "certifi" },
    { name = "urllib3" },
]
sdist = { url = "https://files.pythonhosted.org/packages/40/f0/0e9dc590513d5e742d7799e2038df3a05167cba084c6ca4f3cdd75b55164/sentry_sdk-2.48.0.tar.gz", hash = "sha256:5213190977ff7fdff8a58b722fb807f8d5524a80488626ebeda1b5676c0c1473", size = 384828, upload-time = "2025-12-16T14:55:41.722Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/4d/19/8d77f9992e5cbfcaa9133c3bf63b4fbbb051248802e1e803fed5c552fbb2/sentry_sdk-2.48.0-py2.py3-none-any.whl", hash = "sha256:6b12ac256769d41825d9b7518444e57fa35b5642df4c7c5e322af4d2c8721172", size = 414555, upload-time = "2025-12-16T14:55:40.152Z" },
]

[[package]]
name = "singapore-smb-backend"
version = "0.1.0"
source = { editable = "." }
dependencies = [
    { name = "celery" },
    { name = "django" },
    { name = "django-allauth" },
    { name = "django-cors-headers" },
    { name = "django-environ" },
    { name = "djangorestframework" },
    { name = "drf-spectacular" },
    { name = "gunicorn" },
    { name = "pillow" },
    { name = "psycopg2-binary" },
    { name = "python-jose" },
    { name = "redis" },
    { name = "sentry-sdk" },
    { name = "stripe" },
    { name = "weasyprint" },
]

[package.optional-dependencies]
dev = [
    { name = "black" },
    { name = "factory-boy" },
    { name = "flake8" },
    { name = "isort" },
    { name = "pytest" },
    { name = "pytest-django" },
]

[package.metadata]
requires-dist = [
    { name = "black", marker = "extra == 'dev'", specifier = ">=25.9.0" },
    { name = "celery", specifier = ">=5.5.3" },
    { name = "django", specifier = ">=6.0" },
    { name = "django-allauth", specifier = ">=65.13.1" },
    { name = "django-cors-headers", specifier = ">=4.9.0" },
    { name = "django-environ", specifier = ">=0.12.0" },
    { name = "djangorestframework", specifier = ">=3.16.1" },
    { name = "drf-spectacular", specifier = ">=0.27.1" },
    { name = "factory-boy", marker = "extra == 'dev'", specifier = ">=3.3.3" },
    { name = "flake8", marker = "extra == 'dev'", specifier = ">=7.3.0" },
    { name = "gunicorn", specifier = ">=21.2.0" },
    { name = "isort", marker = "extra == 'dev'", specifier = ">=7.0.0" },
    { name = "pillow", specifier = ">=11.3.0" },
    { name = "psycopg2-binary", specifier = ">=2.9.10" },
    { name = "pytest", marker = "extra == 'dev'", specifier = ">=8.4.2" },
    { name = "pytest-django", marker = "extra == 'dev'", specifier = ">=4.11.1" },
    { name = "python-jose", specifier = ">=3.5.0" },
    { name = "redis", specifier = ">=6.4.0" },
    { name = "sentry-sdk", specifier = ">=2.37.0" },
    { name = "stripe", specifier = ">=8.4.0" },
    { name = "weasyprint", specifier = ">=67.0" },
]
provides-extras = ["dev"]

[[package]]
name = "six"
version = "1.17.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/94/e7/b2c673351809dca68a0e064b6af791aa332cf192da575fd474ed7d6f16a2/six-1.17.0.tar.gz", hash = "sha256:ff70335d468e7eb6ec65b95b99d3a2836546063f63acc5171de367e834932a81", size = 34031, upload-time = "2024-12-04T17:35:28.174Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/b7/ce/149a00dd41f10bc29e5921b496af8b574d8413afcd5e30dfa0ed46c2cc5e/six-1.17.0-py2.py3-none-any.whl", hash = "sha256:4721f391ed90541fddacab5acf947aa0d3dc7d27b2e1e8eda2be8970586c3274", size = 11050, upload-time = "2024-12-04T17:35:26.475Z" },
]

[[package]]
name = "sqlparse"
version = "0.5.4"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/18/67/701f86b28d63b2086de47c942eccf8ca2208b3be69715a1119a4e384415a/sqlparse-0.5.4.tar.gz", hash = "sha256:4396a7d3cf1cd679c1be976cf3dc6e0a51d0111e87787e7a8d780e7d5a998f9e", size = 120112, upload-time = "2025-11-28T07:10:18.377Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/25/70/001ee337f7aa888fb2e3f5fd7592a6afc5283adb1ed44ce8df5764070f22/sqlparse-0.5.4-py3-none-any.whl", hash = "sha256:99a9f0314977b76d776a0fcb8554de91b9bb8a18560631d6bc48721d07023dcb", size = 45933, upload-time = "2025-11-28T07:10:19.73Z" },
]

[[package]]
name = "stripe"
version = "14.1.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "requests" },
    { name = "typing-extensions" },
]
sdist = { url = "https://files.pythonhosted.org/packages/74/db/274e7d6d8a657a6a73ba9306e1e970205a44c6bb2707692a1d67e2ad5458/stripe-14.1.0.tar.gz", hash = "sha256:d002ecd2966a984a52a43e865bc9346c389f20e768e13fdbbe9cb9474f917c23", size = 1449934, upload-time = "2025-12-16T19:54:41.317Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/1a/e6/7202dcb3a0f99e4d1325ccd1000cde86aa6aaa5248ecafbd8c5dca26f70d/stripe-14.1.0-py3-none-any.whl", hash = "sha256:0e687a2eed4d9a66e7602093f7ad02e6c30a0d0c993101848a8c97d7f7607748", size = 2074806, upload-time = "2025-12-16T19:54:39.862Z" },
]

[[package]]
name = "tinycss2"
version = "1.5.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "webencodings" },
]
sdist = { url = "https://files.pythonhosted.org/packages/a3/ae/2ca4913e5c0f09781d75482874c3a95db9105462a92ddd303c7d285d3df2/tinycss2-1.5.1.tar.gz", hash = "sha256:d339d2b616ba90ccce58da8495a78f46e55d4d25f9fd71dfd526f07e7d53f957", size = 88195, upload-time = "2025-11-23T10:29:10.082Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/60/45/c7b5c3168458db837e8ceab06dc77824e18202679d0463f0e8f002143a97/tinycss2-1.5.1-py3-none-any.whl", hash = "sha256:3415ba0f5839c062696996998176c4a3751d18b7edaaeeb658c9ce21ec150661", size = 28404, upload-time = "2025-11-23T10:29:08.676Z" },
]

[[package]]
name = "tinyhtml5"
version = "2.0.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "webencodings" },
]
sdist = { url = "https://files.pythonhosted.org/packages/fd/03/6111ed99e9bf7dfa1c30baeef0e0fb7e0bd387bd07f8e5b270776fe1de3f/tinyhtml5-2.0.0.tar.gz", hash = "sha256:086f998833da24c300c414d9fe81d9b368fd04cb9d2596a008421cbc705fcfcc", size = 179507, upload-time = "2024-10-29T15:37:14.078Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/5c/de/27c57899297163a4a84104d5cec0af3b1ac5faf62f44667e506373c6b8ce/tinyhtml5-2.0.0-py3-none-any.whl", hash = "sha256:13683277c5b176d070f82d099d977194b7a1e26815b016114f581a74bbfbf47e", size = 39793, upload-time = "2024-10-29T15:37:11.743Z" },
]

[[package]]
name = "typing-extensions"
version = "4.15.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/72/94/1a15dd82efb362ac84269196e94cf00f187f7ed21c242792a923cdb1c61f/typing_extensions-4.15.0.tar.gz", hash = "sha256:0cea48d173cc12fa28ecabc3b837ea3cf6f38c6d1136f85cbaaf598984861466", size = 109391, upload-time = "2025-08-25T13:49:26.313Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/18/67/36e9267722cc04a6b9f15c7f3441c2363321a3ea07da7ae0c0707beb2a9c/typing_extensions-4.15.0-py3-none-any.whl", hash = "sha256:f0fa19c6845758ab08074a0cfa8b7aecb71c999ca73d62883bc25cc018c4e548", size = 44614, upload-time = "2025-08-25T13:49:24.86Z" },
]

[[package]]
name = "tzdata"
version = "2025.3"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/5e/a7/c202b344c5ca7daf398f3b8a477eeb205cf3b6f32e7ec3a6bac0629ca975/tzdata-2025.3.tar.gz", hash = "sha256:de39c2ca5dc7b0344f2eba86f49d614019d29f060fc4ebc8a417896a620b56a7", size = 196772, upload-time = "2025-12-13T17:45:35.667Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/c7/b0/003792df09decd6849a5e39c28b513c06e84436a54440380862b5aeff25d/tzdata-2025.3-py2.py3-none-any.whl", hash = "sha256:06a47e5700f3081aab02b2e513160914ff0694bce9947d6b76ebd6bf57cfc5d1", size = 348521, upload-time = "2025-12-13T17:45:33.889Z" },
]

[[package]]
name = "tzlocal"
version = "5.3.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "tzdata", marker = "sys_platform == 'win32'" },
]
sdist = { url = "https://files.pythonhosted.org/packages/8b/2e/c14812d3d4d9cd1773c6be938f89e5735a1f11a9f184ac3639b93cef35d5/tzlocal-5.3.1.tar.gz", hash = "sha256:cceffc7edecefea1f595541dbd6e990cb1ea3d19bf01b2809f362a03dd7921fd", size = 30761, upload-time = "2025-03-05T21:17:41.549Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/c2/14/e2a54fabd4f08cd7af1c07030603c3356b74da07f7cc056e600436edfa17/tzlocal-5.3.1-py3-none-any.whl", hash = "sha256:eb1a66c3ef5847adf7a834f1be0800581b683b5608e74f86ecbcef8ab91bb85d", size = 18026, upload-time = "2025-03-05T21:17:39.857Z" },
]

[[package]]
name = "uritemplate"
version = "4.2.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/98/60/f174043244c5306c9988380d2cb10009f91563fc4b31293d27e17201af56/uritemplate-4.2.0.tar.gz", hash = "sha256:480c2ed180878955863323eea31b0ede668795de182617fef9c6ca09e6ec9d0e", size = 33267, upload-time = "2025-06-02T15:12:06.318Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/a9/99/3ae339466c9183ea5b8ae87b34c0b897eda475d2aec2307cae60e5cd4f29/uritemplate-4.2.0-py3-none-any.whl", hash = "sha256:962201ba1c4edcab02e60f9a0d3821e82dfc5d2d6662a21abd533879bdb8a686", size = 11488, upload-time = "2025-06-02T15:12:03.405Z" },
]

[[package]]
name = "urllib3"
version = "2.6.2"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/1e/24/a2a2ed9addd907787d7aa0355ba36a6cadf1768b934c652ea78acbd59dcd/urllib3-2.6.2.tar.gz", hash = "sha256:016f9c98bb7e98085cb2b4b17b87d2c702975664e4f060c6532e64d1c1a5e797", size = 432930, upload-time = "2025-12-11T15:56:40.252Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/6d/b9/4095b668ea3678bf6a0af005527f39de12fb026516fb3df17495a733b7f8/urllib3-2.6.2-py3-none-any.whl", hash = "sha256:ec21cddfe7724fc7cb4ba4bea7aa8e2ef36f607a4bab81aa6ce42a13dc3f03dd", size = 131182, upload-time = "2025-12-11T15:56:38.584Z" },
]

[[package]]
name = "vine"
version = "5.1.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/bd/e4/d07b5f29d283596b9727dd5275ccbceb63c44a1a82aa9e4bfd20426762ac/vine-5.1.0.tar.gz", hash = "sha256:8b62e981d35c41049211cf62a0a1242d8c1ee9bd15bb196ce38aefd6799e61e0", size = 48980, upload-time = "2023-11-05T08:46:53.857Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/03/ff/7c0c86c43b3cbb927e0ccc0255cb4057ceba4799cd44ae95174ce8e8b5b2/vine-5.1.0-py3-none-any.whl", hash = "sha256:40fdf3c48b2cfe1c38a49e9ae2da6fda88e4794c810050a728bd7413811fb1dc", size = 9636, upload-time = "2023-11-05T08:46:51.205Z" },
]

[[package]]
name = "wcwidth"
version = "0.2.14"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/24/30/6b0809f4510673dc723187aeaf24c7f5459922d01e2f794277a3dfb90345/wcwidth-0.2.14.tar.gz", hash = "sha256:4d478375d31bc5395a3c55c40ccdf3354688364cd61c4f6adacaa9215d0b3605", size = 102293, upload-time = "2025-09-22T16:29:53.023Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/af/b5/123f13c975e9f27ab9c0770f514345bd406d0e8d3b7a0723af9d43f710af/wcwidth-0.2.14-py2.py3-none-any.whl", hash = "sha256:a7bb560c8aee30f9957e5f9895805edd20602f2d7f720186dfd906e82b4982e1", size = 37286, upload-time = "2025-09-22T16:29:51.641Z" },
]

[[package]]
name = "weasyprint"
version = "67.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "cffi" },
    { name = "cssselect2" },
    { name = "fonttools", extra = ["woff"] },
    { name = "pillow" },
    { name = "pydyf" },
    { name = "pyphen" },
    { name = "tinycss2" },
    { name = "tinyhtml5" },
]
sdist = { url = "https://files.pythonhosted.org/packages/fd/bc/79a65b3a406cb62a1982fec8b49134b25a3b31abb094ca493c9fddff5492/weasyprint-67.0.tar.gz", hash = "sha256:fdfbccf700e8086c8fd1607ec42e25d4b584512c29af2d9913587a4e448dead4", size = 1534152, upload-time = "2025-12-02T16:11:36.972Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/1e/3a/a225e214ae2accd8781e4d22e9397bd51290c631ea0943d3a0a1840bc667/weasyprint-67.0-py3-none-any.whl", hash = "sha256:abc2f40872ea01c29c11f7799dafc4b23c078335bf7777f72a8affeb36e1d201", size = 316309, upload-time = "2025-12-02T16:11:35.402Z" },
]

[[package]]
name = "webencodings"
version = "0.5.1"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/0b/02/ae6ceac1baeda530866a85075641cec12989bd8d31af6d5ab4a3e8c92f47/webencodings-0.5.1.tar.gz", hash = "sha256:b36a1c245f2d304965eb4e0a82848379241dc04b865afcc4aab16748587e1923", size = 9721, upload-time = "2017-04-05T20:21:34.189Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/f4/24/2a3e3df732393fed8b3ebf2ec078f05546de641fe1b667ee316ec1dcf3b7/webencodings-0.5.1-py2.py3-none-any.whl", hash = "sha256:a0af1213f3c2226497a97e2b3aa01a7e4bee4f403f95be16fc9acd2947514a78", size = 11774, upload-time = "2017-04-05T20:21:32.581Z" },
]

[[package]]
name = "zopfli"
version = "0.4.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/be/4c/efa0760686d4cc69e68a8f284d3c6c5884722c50f810af0e277fb7d61621/zopfli-0.4.0.tar.gz", hash = "sha256:a8ee992b2549e090cd3f0178bf606dd41a29e0613a04cdf5054224662c72dce6", size = 176720, upload-time = "2025-11-07T17:00:59.507Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/98/62/ec5cb67ee379c6a4f296f1277b971ff8c26460bf8775f027f82c519a0a72/zopfli-0.4.0-cp310-abi3-macosx_10_9_universal2.whl", hash = "sha256:d1b98ad47c434ef213444a03ef2f826eeec100144d64f6a57504b9893d3931ce", size = 287433, upload-time = "2025-11-07T17:00:45.662Z" },
    { url = "https://files.pythonhosted.org/packages/5a/9e/8f81e69bd771014a488c4c64476b6e6faab91b2c913d0f81eca7e06401eb/zopfli-0.4.0-cp310-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:18b5f1570f64d4988482e4466f10ef5f2a30f687c19ad62a64560f2152dc89eb", size = 847135, upload-time = "2025-11-07T17:00:47.483Z" },
    { url = "https://files.pythonhosted.org/packages/24/84/6e60eeaaa1c1eae7b4805f1c528f3e8ae62cef323ec1e52347a11031e3ba/zopfli-0.4.0-cp310-abi3-manylinux_2_24_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:b72a010d205d00b2855acc2302772067362f9ab5a012e3550662aec60d28e6b3", size = 831606, upload-time = "2025-11-07T17:00:48.576Z" },
    { url = "https://files.pythonhosted.org/packages/6d/aa/a4d5de7ed8e809953cb5e8992bddc40f38461ec5a44abfb010953875adfc/zopfli-0.4.0-cp310-abi3-musllinux_1_2_aarch64.whl", hash = "sha256:c3ba02a9a6ca90481d2b2f68bab038b310d63a1e3b5ae305e95a6599787ed941", size = 1789376, upload-time = "2025-11-07T17:00:49.63Z" },
    { url = "https://files.pythonhosted.org/packages/39/95/4d1e943fbc44157f58b623625686d0b970f2fda269e721fbf9546b93f6cc/zopfli-0.4.0-cp310-abi3-musllinux_1_2_x86_64.whl", hash = "sha256:7d66337be6d5613dec55213e9ac28f378c41e2cc04fbad4a10748e4df774ca85", size = 1879013, upload-time = "2025-11-07T17:00:50.751Z" },
    { url = "https://files.pythonhosted.org/packages/95/db/4f2eebf73c0e2df293a366a1d176cd315a74ce0b00f83826a7ba9ddd1ab3/zopfli-0.4.0-cp310-abi3-win32.whl", hash = "sha256:03181d48e719fcb6cf8340189c61e8f9883d8bbbdf76bf5212a74457f7d083c1", size = 83655, upload-time = "2025-11-07T17:00:51.797Z" },
    { url = "https://files.pythonhosted.org/packages/24/f6/bd80c5278b1185dc41155c77bc61bfe1d817254a7f2115f66aa69a270b89/zopfli-0.4.0-cp310-abi3-win_amd64.whl", hash = "sha256:f94e4dd7d76b4fe9f5d9229372be20d7f786164eea5152d1af1c34298c3d5975", size = 100824, upload-time = "2025-11-07T17:00:52.658Z" },
]

```

# backend/core/__init__.py
```py
"""
Core module for Singapore SMB E-commerce Platform.

This module provides shared infrastructure components used across all apps.
"""

```

# backend/core/exceptions.py
```py
"""
Custom exceptions for Singapore SMB E-commerce Platform.

These exceptions provide structured error handling with:
- Consistent error codes for API responses
- Clear error messages for debugging
- Proper HTTP status codes
"""
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler
from rest_framework.response import Response


# =============================================================================
# BASE EXCEPTIONS
# =============================================================================

class BusinessLogicError(APIException):
    """
    Base exception for business logic errors.
    
    Use this as the parent class for domain-specific exceptions.
    Returns HTTP 400 by default.
    """
    status_code = 400
    default_code = 'business_error'
    default_detail = 'A business logic error occurred.'


class ValidationError(BusinessLogicError):
    """
    Raised when business rule validation fails.
    
    Examples:
        - Invalid GST code
        - Order amount below minimum
        - Invalid date range
    """
    default_code = 'validation_error'
    default_detail = 'Validation failed.'


# =============================================================================
# COMMERCE EXCEPTIONS
# =============================================================================

class InsufficientStockError(BusinessLogicError):
    """
    Raised when inventory is insufficient for an operation.
    
    Attributes:
        product_id: ID of the product with insufficient stock
        requested: Quantity requested
        available: Quantity available
    """
    default_code = 'insufficient_stock'
    default_detail = 'Insufficient stock available.'
    
    def __init__(self, product_id=None, requested=None, available=None, detail=None):
        if detail is None and product_id:
            detail = f'Insufficient stock for product {product_id}. Requested: {requested}, Available: {available}'
        super().__init__(detail=detail)
        self.product_id = product_id
        self.requested = requested
        self.available = available


class OrderStateError(BusinessLogicError):
    """
    Raised when an order state transition is invalid.
    
    Example: Trying to ship an already cancelled order.
    """
    default_code = 'invalid_order_state'
    default_detail = 'Invalid order state transition.'


# =============================================================================
# PAYMENT EXCEPTIONS
# =============================================================================

class PaymentError(BusinessLogicError):
    """
    Base exception for payment processing errors.
    
    Returns HTTP 402 Payment Required.
    """
    status_code = 402
    default_code = 'payment_error'
    default_detail = 'Payment processing failed.'


class PaymentDeclinedError(PaymentError):
    """Raised when a payment is declined by the gateway."""
    default_code = 'payment_declined'
    default_detail = 'Your payment was declined. Please try a different payment method.'


class PaymentGatewayError(PaymentError):
    """Raised when the payment gateway is unavailable."""
    status_code = 503
    default_code = 'gateway_unavailable'
    default_detail = 'Payment service is temporarily unavailable.'


# =============================================================================
# AUTHENTICATION EXCEPTIONS
# =============================================================================

class AuthenticationError(BusinessLogicError):
    """Base exception for authentication errors."""
    status_code = 401
    default_code = 'authentication_error'
    default_detail = 'Authentication failed.'


class AccountLockedError(AuthenticationError):
    """Raised when a user account is locked due to failed attempts."""
    default_code = 'account_locked'
    default_detail = 'Account is locked due to too many failed login attempts.'


class MFARequiredError(AuthenticationError):
    """Raised when MFA verification is required."""
    default_code = 'mfa_required'
    default_detail = 'Multi-factor authentication is required.'


# =============================================================================
# AUTHORIZATION EXCEPTIONS
# =============================================================================

class PermissionDeniedError(BusinessLogicError):
    """Raised when user lacks required permissions."""
    status_code = 403
    default_code = 'permission_denied'
    default_detail = 'You do not have permission to perform this action.'


class TenantAccessError(PermissionDeniedError):
    """Raised when user tries to access another company's data."""
    default_code = 'tenant_access_denied'
    default_detail = 'Access to this resource is not permitted.'


# =============================================================================
# INTEGRATION EXCEPTIONS
# =============================================================================

class IntegrationError(BusinessLogicError):
    """Base exception for third-party integration errors."""
    status_code = 502
    default_code = 'integration_error'
    default_detail = 'An error occurred with an external service.'


class LogisticsError(IntegrationError):
    """Raised when logistics provider API fails."""
    default_code = 'logistics_error'
    default_detail = 'Shipping service error.'


class GSTError(BusinessLogicError):
    """Raised for GST calculation or validation errors."""
    default_code = 'gst_error'
    default_detail = 'GST processing error.'


# =============================================================================
# CUSTOM EXCEPTION HANDLER
# =============================================================================

def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF that provides consistent error responses.
    
    Response format:
    {
        "status": "error",
        "error": {
            "code": "error_code",
            "message": "Human-readable message",
            "details": [...] (optional)
        }
    }
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        # Build custom error response
        error_data = {
            'status': 'error',
            'error': {
                'code': getattr(exc, 'default_code', 'error'),
                'message': str(exc.detail) if hasattr(exc, 'detail') else str(exc),
            }
        }
        
        # Add details if available (e.g., validation errors)
        if hasattr(exc, 'detail') and isinstance(exc.detail, dict):
            error_data['error']['details'] = exc.detail
        
        response.data = error_data
    
    return response

```

# backend/core/middleware.py
```py
"""
Custom middleware for Singapore SMB E-commerce Platform.

Provides:
- TenantMiddleware: Multi-tenant context management
- AuditMiddleware: Track current user for audit fields
- SecurityHeadersMiddleware: Add security headers to responses
"""
import threading
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse


# Thread-local storage for request context
_thread_locals = threading.local()


def get_current_user():
    """Get the current user from thread-local storage."""
    return getattr(_thread_locals, 'user', None)


def get_current_company():
    """Get the current company from thread-local storage."""
    return getattr(_thread_locals, 'company', None)


def get_current_request():
    """Get the current request from thread-local storage."""
    return getattr(_thread_locals, 'request', None)


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware that sets the current company context for multi-tenant isolation.
    
    Extracts company from:
    1. JWT token claims
    2. User's associated company
    3. X-Company-ID header (for internal services)
    
    Sets company in thread-local storage for use in queries.
    """
    
    def process_request(self, request):
        """Extract and set company context."""
        company = None
        
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Get company from authenticated user
            company = getattr(request.user, 'company', None)
        
        # Allow header override for internal services
        company_header = request.headers.get('X-Company-ID')
        if company_header and hasattr(request, 'user'):
            if request.user.is_superuser:
                from apps.accounts.models import Company
                try:
                    company = Company.objects.get(id=company_header)
                except Company.DoesNotExist:
                    pass
        
        # Store in thread-local
        _thread_locals.company = company
        request.company = company
    
    def process_response(self, request, response):
        """Clean up thread-local storage."""
        if hasattr(_thread_locals, 'company'):
            del _thread_locals.company
        return response


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware that stores current user and request for audit logging.
    
    Makes the current user available to models for automatic
    population of created_by/updated_by fields.
    """
    
    def process_request(self, request):
        """Store user and request in thread-local storage."""
        _thread_locals.request = request
        _thread_locals.user = getattr(request, 'user', None)
    
    def process_response(self, request, response):
        """Clean up thread-local storage."""
        if hasattr(_thread_locals, 'user'):
            del _thread_locals.user
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware that adds security headers to all responses.
    
    Headers added:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy: Restrict browser features
    """
    
    def process_response(self, request, response):
        """Add security headers to response."""
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # XSS protection (legacy, but still useful)
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions policy (restrict browser features)
        response['Permissions-Policy'] = (
            'accelerometer=(), camera=(), geolocation=(), gyroscope=(), '
            'magnetometer=(), microphone=(), payment=(), usb=()'
        )
        
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware that logs API requests for debugging and monitoring.
    
    Logs:
    - Request method and path
    - User ID (if authenticated)
    - Response status code
    - Request duration
    """
    
    def process_request(self, request):
        """Record request start time."""
        import time
        request._start_time = time.time()
    
    def process_response(self, request, response):
        """Log request details."""
        import logging
        import time
        
        logger = logging.getLogger('apps')
        
        # Calculate duration
        duration = None
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
        
        # Build log message
        user_id = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_id = str(request.user.id)
        
        # Only log API requests
        if request.path.startswith('/api/'):
            logger.info(
                f"{request.method} {request.path} "
                f"[{response.status_code}] "
                f"user={user_id} "
                f"duration={duration:.3f}s" if duration else ""
            )
        
        return response


class APIVersionMiddleware(MiddlewareMixin):
    """
    Middleware that adds API version info to responses.
    
    Adds X-API-Version header to all API responses.
    """
    
    def process_response(self, request, response):
        """Add API version header."""
        if request.path.startswith('/api/'):
            response['X-API-Version'] = '1.0'
        return response


class MaintenanceModeMiddleware(MiddlewareMixin):
    """
    Middleware that enables maintenance mode.
    
    When MAINTENANCE_MODE setting is True, returns 503 for all
    non-admin requests.
    """
    
    def process_request(self, request):
        """Check maintenance mode."""
        from django.conf import settings
        
        if getattr(settings, 'MAINTENANCE_MODE', False):
            # Allow admin access
            if request.path.startswith('/admin/'):
                return None
            
            # Allow health check
            if request.path == '/health/':
                return None
            
            return JsonResponse(
                {
                    'status': 'error',
                    'error': {
                        'code': 'maintenance',
                        'message': 'System is under maintenance. Please try again later.',
                    }
                },
                status=503
            )
        
        return None

```

# backend/core/models.py
```py
"""
Core abstract models for Singapore SMB E-commerce Platform.

These base models provide common fields and functionality for all models:
- UUID primary keys for distributed-friendly IDs
- Automatic timestamp tracking
- Audit fields for user tracking
- Soft delete support
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class BaseModel(models.Model):
    """
    Abstract base model with UUID primary key and timestamps.
    
    All models should inherit from this to ensure consistent:
    - UUID-based primary keys (distributed-friendly)
    - Creation and modification timestamps
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier (UUID4)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this record was last updated"
    )
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
    
    def __str__(self):
        return str(self.id)


class AuditableModel(BaseModel):
    """
    Abstract model that tracks which user created/modified records.
    
    Use for models where accountability and audit trails are important.
    Automatically populated via middleware or manual assignment.
    """
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        help_text="User who created this record"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        help_text="User who last modified this record"
    )
    
    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    """
    Manager that excludes soft-deleted records by default.
    
    Use `.all_with_deleted()` to include deleted records.
    """
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)
    
    def all_with_deleted(self):
        """Return all records including soft-deleted ones."""
        return super().get_queryset()
    
    def deleted_only(self):
        """Return only soft-deleted records."""
        return super().get_queryset().filter(deleted_at__isnull=False)


class SoftDeleteModel(BaseModel):
    """
    Abstract model with soft delete functionality.
    
    Instead of permanently deleting records, sets `deleted_at` timestamp.
    PDPA compliance: Allows data retention while marking as "deleted".
    
    Methods:
        delete(): Soft-delete the record
        hard_delete(): Permanently delete the record
        restore(): Restore a soft-deleted record
    """
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When this record was soft-deleted"
    )
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Access all records including deleted
    
    class Meta:
        abstract = True
    
    @property
    def is_deleted(self) -> bool:
        """Check if record is soft-deleted."""
        return self.deleted_at is not None
    
    def delete(self, using=None, keep_parents=False):
        """
        Soft-delete the record by setting deleted_at timestamp.
        
        For permanent deletion, use hard_delete().
        """
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at', 'updated_at'])
    
    def hard_delete(self, using=None, keep_parents=False):
        """
        Permanently delete the record from the database.
        
        WARNING: This cannot be undone!
        """
        super().delete(using=using, keep_parents=keep_parents)
    
    def restore(self):
        """Restore a soft-deleted record."""
        if self.deleted_at is not None:
            self.deleted_at = None
            self.save(update_fields=['deleted_at', 'updated_at'])


class CompanyOwnedModel(SoftDeleteModel):
    """
    Abstract model for records that belong to a specific company.
    
    Provides multi-tenant data isolation when combined with
    TenantMiddleware and appropriate permissions.
    """
    company = models.ForeignKey(
        'accounts.Company',
        on_delete=models.CASCADE,
        related_name='%(class)s_set',
        help_text="Company that owns this record"
    )
    
    class Meta:
        abstract = True

```

# backend/core/permissions.py
```py
"""
Custom DRF permissions for Singapore SMB E-commerce Platform.

Provides:
- Tenant isolation (IsCompanyMember)
- Role-based access control (HasRole, HasAnyRole)
- Object-level permissions (IsOwnerOrAdmin)
"""
from rest_framework.permissions import BasePermission


class IsCompanyMember(BasePermission):
    """
    Permission that ensures user belongs to the company in the request.
    
    Used for multi-tenant data isolation. Checks that the authenticated
    user's company matches the company_id in the URL or request data.
    """
    message = "You do not have access to this company's resources."
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Superusers bypass company check
        if request.user.is_superuser:
            return True
        
        # Get company_id from URL kwargs or request data
        company_id = (
            view.kwargs.get('company_id') or
            request.data.get('company_id') or
            request.query_params.get('company_id')
        )
        
        if company_id is None:
            # If no company_id specified, use user's company
            return True
        
        return str(request.user.company_id) == str(company_id)
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Check if object has company attribute
        if hasattr(obj, 'company_id'):
            return obj.company_id == request.user.company_id
        
        return True


class HasRole(BasePermission):
    """
    Permission that checks if user has a specific role.
    
    Usage in ViewSet:
        permission_classes = [HasRole]
        required_roles = ['admin', 'finance']
    
    Or use HasAnyRole for inline usage.
    """
    message = "You do not have the required role to perform this action."
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Get required roles from view
        required_roles = getattr(view, 'required_roles', [])
        
        if not required_roles:
            return True
        
        # Check if user has any of the required roles
        user_roles = set(request.user.roles.values_list('name', flat=True))
        return bool(user_roles.intersection(set(required_roles)))


def HasAnyRole(*roles):
    """
    Factory function to create a permission class requiring any of the given roles.
    
    Usage:
        permission_classes = [HasAnyRole('admin', 'owner')]
    """
    class HasAnyRolePermission(BasePermission):
        message = f"Required role: one of {roles}"
        
        def has_permission(self, request, view):
            if not request.user.is_authenticated:
                return False
            
            if request.user.is_superuser:
                return True
            
            user_roles = set(request.user.roles.values_list('name', flat=True))
            return bool(user_roles.intersection(set(roles)))
    
    return HasAnyRolePermission


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission that allows access only to:
    - Object owner (via user field)
    - Admins
    - Superusers
    
    Configure the owner field via view attribute:
        owner_field = 'created_by'  # Default: 'user'
    """
    message = "You do not have permission to access this object."
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Check if user is admin
        if hasattr(request.user, 'roles'):
            if request.user.roles.filter(name='admin').exists():
                return True
        
        # Check ownership
        owner_field = getattr(view, 'owner_field', 'user')
        
        if hasattr(obj, owner_field):
            owner = getattr(obj, owner_field)
            if owner is not None:
                owner_id = owner.id if hasattr(owner, 'id') else owner
                return owner_id == request.user.id
        
        return False


class IsAdminUser(BasePermission):
    """
    Permission that allows access only to admin users.
    
    Checks:
    - is_superuser flag
    - 'admin' role assignment
    """
    message = "Admin access required."
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        if hasattr(request.user, 'roles'):
            return request.user.roles.filter(name='admin').exists()
        
        return False


class IsFinanceUser(BasePermission):
    """
    Permission for finance-sensitive operations like GST filing.
    
    Allows:
    - Superusers
    - Users with 'finance' or 'admin' role
    """
    message = "Finance role required for this operation."
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        if hasattr(request.user, 'roles'):
            return request.user.roles.filter(
                name__in=['finance', 'admin', 'owner']
            ).exists()
        
        return False


class ReadOnly(BasePermission):
    """
    Permission that allows read-only access (GET, HEAD, OPTIONS).
    
    Useful for public endpoints or combining with other permissions.
    """
    def has_permission(self, request, view):
        return request.method in ('GET', 'HEAD', 'OPTIONS')

```

# backend/manage.py
```py
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

```

# backend/README.md
```md
# Singapore SMB E-commerce Platform (Hybrid Architecture)

## Overview
A comprehensive e-commerce and inventory management system designed for Singapore SMBs, featuring:
- **Backend**: Django 5.2+ (Python) for financial precision, GST compliance, and admin operations.
- **Frontend**: Next.js 16+ (React) for a high-performance, mobile-first PWA storefront.
- **Compliance**: Built-in support for Singapore GST (F5), InvoiceNow (PEPPOL), and PDPA.

## Project Structure
- `backend/`: Django API, Celery workers, and Business Logic.
- `frontend/`: Next.js PWA, Customer Storefront.

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+

### Backend Setup
```bash
cd backend
pip install -e .
python manage.py migrate
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

```

# backend/conftest.py
```py
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.development"
python_files = ["tests.py", "test_*.py", "*_tests.py"]
addopts = "--strict-markers --tb=short -v"
testpaths = ["apps"]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests"
]

[tool.coverage.run]
source = ["apps"]
omit = ["*/tests/*", "*/migrations/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
]

```

# backend/pyproject.toml
```toml
[project]
name = "singapore-smb-backend"
version = "0.1.0"
description = "Django backend for Singapore SMB E-commerce Platform"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "Django>=6.0",
    "djangorestframework>=3.16.1",
    "djangorestframework-simplejwt>=5.4.0",  # JWT Authentication
    "django-cors-headers>=4.9.0",
    "django-environ>=0.12.0",
    "django-allauth>=65.13.1",
    "django-debug-toolbar>=4.5.0",  # Development debugging
    "celery>=5.5.3",
    "redis>=6.4.0",
    "psycopg2-binary>=2.9.10",
    "gunicorn>=21.2.0",
    "pillow>=11.3.0",
    "drf-spectacular>=0.27.1",  # For API Documentation
    "stripe>=8.4.0",            # Payment Processing
    "weasyprint>=67.0",         # Invoice PDF Generation
    "python-jose>=3.5.0", # JWT Handling
    "sentry-sdk>=2.37.0"        # Error Monitoring
]

[project.optional-dependencies]
dev = [
    "pytest>=8.4.2",
    "pytest-django>=4.11.1",
    "pytest-cov>=6.2.0",
    "black>=25.9.0",
    "isort>=7.0.0",
    "flake8>=7.3.0",
    "factory-boy>=3.3.3"
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["config", "apps"]

```

# backend/pytest.ini
```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.development
python_files = tests.py test_*.py *_tests.py
addopts = 
    --strict-markers
    --tb=short
    -v
testpaths = apps
filterwarnings =
    ignore::DeprecationWarning
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests

```

# backend/config/__init__.py
```py
"""
Django project configuration package.

This module initializes the Celery application for the project.
"""
from .celery import app as celery_app

__all__ = ('celery_app',)

```

# backend/config/settings/__init__.py
```py
"""Settings package for different environments."""

```

# backend/config/settings/development.py
```py
"""
Django development settings.

These settings extend base.py for local development.
"""
from .base import *  # noqa: F401, F403

# =============================================================================
# DEBUG
# =============================================================================

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# =============================================================================
# DATABASE
# =============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='singapore_smb'),
        'USER': env('DB_USER', default='postgres'),
        'PASSWORD': env('DB_PASSWORD', default='postgres'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
    }
}

# =============================================================================
# DEBUG TOOLBAR
# =============================================================================

INSTALLED_APPS += ['debug_toolbar']  # noqa: F405
MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa: F405
INTERNAL_IPS = ['127.0.0.1']

# =============================================================================
# CORS
# =============================================================================

CORS_ALLOW_ALL_ORIGINS = True

# =============================================================================
# EMAIL (Console backend for development)
# =============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# =============================================================================
# LOGGING
# =============================================================================

LOGGING['handlers']['console']['level'] = 'DEBUG'  # noqa: F405
LOGGING['loggers']['apps']['level'] = 'DEBUG'  # noqa: F405

# =============================================================================
# DJANGO REST FRAMEWORK
# =============================================================================

# Add browsable API for development
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [  # noqa: F405
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
]

# =============================================================================
# JWT (Longer-lived tokens for development)
# =============================================================================

from datetime import timedelta
SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(hours=1)  # noqa: F405
SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'] = timedelta(days=30)  # noqa: F405

```

# backend/config/settings/base.py
```py
"""
Django base settings for Singapore SMB E-commerce Platform.

These settings are shared across all environments.
For production deployment, use production.py which extends these settings.
"""
import os
from decimal import Decimal
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
)

# Read .env file if it exists
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# =============================================================================
# SECURITY SETTINGS
# =============================================================================

SECRET_KEY = env('SECRET_KEY', default='django-insecure-dev-key-change-in-production')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# =============================================================================
# APPLICATION DEFINITION
# =============================================================================

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    # Django REST Framework
    'rest_framework',
    'corsheaders',
    
    # Authentication
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    
    # API Documentation
    'drf_spectacular',
]

LOCAL_APPS = [
    'core',
    'apps.accounts',
    # Future apps:
    # 'apps.commerce',
    # 'apps.inventory',
    # 'apps.accounting',
    # 'apps.compliance',
    # 'apps.payments',
    # 'apps.integrations',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# =============================================================================
# MIDDLEWARE
# =============================================================================

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    # Custom middleware (add after implementation)
    # 'core.middleware.TenantMiddleware',
    # 'core.middleware.AuditMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# =============================================================================
# DATABASE
# =============================================================================

DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default='postgres://postgres:postgres@localhost:5432/singapore_smb'
    )
}

# Ensure decimal precision for financial data
DATABASES['default']['OPTIONS'] = {
    'options': '-c statement_timeout=30000'  # 30 second query timeout
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# AUTHENTICATION
# =============================================================================

AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# django-allauth settings
SITE_ID = 1
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_USER_MODEL_USERNAME_FIELD = None

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 10},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# =============================================================================
# REST FRAMEWORK
# =============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# =============================================================================
# API DOCUMENTATION (drf-spectacular)
# =============================================================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'Singapore SMB E-commerce API',
    'DESCRIPTION': 'API for managing e-commerce, inventory, and accounting for Singapore SMBs',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/v[0-9]',
}

# =============================================================================
# CACHE
# =============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://localhost:6379/0'),
    }
}

# =============================================================================
# CELERY
# =============================================================================

CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://localhost:6379/1')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Singapore'
CELERY_ENABLE_UTC = True

# Task routing
CELERY_TASK_ROUTES = {
    'apps.commerce.tasks.*': {'queue': 'commerce'},
    'apps.inventory.tasks.*': {'queue': 'inventory'},
    'apps.accounting.tasks.*': {'queue': 'accounting'},
    'apps.payments.tasks.*': {'queue': 'payments'},
}

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = 'en-sg'
TIME_ZONE = 'Asia/Singapore'
USE_I18N = True
USE_TZ = True

# =============================================================================
# STATIC AND MEDIA FILES
# =============================================================================

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =============================================================================
# CORS
# =============================================================================

CORS_ALLOWED_ORIGINS = env.list(
    'CORS_ALLOWED_ORIGINS',
    default=['http://localhost:3000', 'http://127.0.0.1:3000']
)

# =============================================================================
# LOGGING
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# =============================================================================
# BUSINESS SETTINGS - SINGAPORE SPECIFIC
# =============================================================================

# GST Configuration
GST_RATE = Decimal('0.09')  # 9% as of January 1, 2024
GST_REGISTRATION_THRESHOLD = Decimal('1000000')  # S$1,000,000

# GST Codes
GST_CODES = [
    ('SR', 'Standard Rated (9%)'),
    ('ZR', 'Zero Rated (0%)'),
    ('ES', 'Exempt Supply'),
    ('OS', 'Out of Scope'),
]

# Financial precision settings
DECIMAL_MAX_DIGITS = 12
DECIMAL_PLACES = 2
GST_RATE_DECIMAL_PLACES = 4

# Platform settings
PLATFORM_NAME = 'Singapore SMB E-commerce Platform'
PLATFORM_VERSION = '1.0.0'

```

# backend/config/settings/production.py
```py
"""
Django production settings.

These settings extend base.py for production deployment.
SECURITY WARNING: Review all settings before deploying to production!
"""
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .base import *  # noqa: F401, F403

# =============================================================================
# DEBUG
# =============================================================================

DEBUG = False
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# =============================================================================
# SECURITY
# =============================================================================

# HTTPS/SSL
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# HSTS
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content security
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# =============================================================================
# DATABASE
# =============================================================================

DATABASES = {
    'default': env.db('DATABASE_URL')
}

# Connection pooling for production
DATABASES['default']['CONN_MAX_AGE'] = 60
DATABASES['default']['CONN_HEALTH_CHECKS'] = True

# =============================================================================
# CACHE
# =============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session using cache
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# =============================================================================
# CORS
# =============================================================================

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS')

# =============================================================================
# SENTRY ERROR TRACKING
# =============================================================================

SENTRY_DSN = env('SENTRY_DSN', default='')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
        send_default_pii=False,  # PDPA compliance
        environment=env('ENVIRONMENT', default='production'),
    )

# =============================================================================
# EMAIL
# =============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = True

# =============================================================================
# STATIC FILES
# =============================================================================

# Use WhiteNoise for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')  # noqa: F405
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# =============================================================================
# LOGGING
# =============================================================================

LOGGING['handlers']['file']['filename'] = '/var/log/django/django.log'  # noqa: F405
LOGGING['root']['level'] = 'WARNING'  # noqa: F405

```

# backend/config/wsgi.py
```py
"""
WSGI config for Singapore SMB E-commerce Platform.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_wsgi_application()

```

# backend/config/asgi.py
```py
"""
ASGI config for Singapore SMB E-commerce Platform.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_asgi_application()

```

# backend/config/celery.py
```py
"""
Celery configuration for Singapore SMB E-commerce Platform.

This module configures the Celery application for asynchronous task processing.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Create Celery app
app = Celery('singapore_smb')

# Configure Celery using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from installed apps
app.autodiscover_tasks()

# =============================================================================
# TASK QUEUES
# =============================================================================

app.conf.task_queues = {
    'default': {
        'exchange': 'default',
        'routing_key': 'default',
    },
    'commerce': {
        'exchange': 'commerce',
        'routing_key': 'commerce',
    },
    'inventory': {
        'exchange': 'inventory',
        'routing_key': 'inventory',
    },
    'accounting': {
        'exchange': 'accounting',
        'routing_key': 'accounting',
    },
    'payments': {
        'exchange': 'payments',
        'routing_key': 'payments',
    },
    'notifications': {
        'exchange': 'notifications',
        'routing_key': 'notifications',
    },
}

# =============================================================================
# BEAT SCHEDULE (Periodic Tasks)
# =============================================================================

app.conf.beat_schedule = {
    # Inventory tasks
    'check-low-stock-every-15-mins': {
        'task': 'apps.inventory.tasks.check_low_stock',
        'schedule': crontab(minute='*/15'),
    },
    'cleanup-expired-reservations': {
        'task': 'apps.inventory.tasks.cleanup_expired_reservations',
        'schedule': crontab(minute='*/5'),
    },
    
    # Commerce tasks
    'cleanup-abandoned-carts-daily': {
        'task': 'apps.commerce.tasks.cleanup_abandoned_carts',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
    
    # Accounting tasks
    'generate-daily-reports': {
        'task': 'apps.accounting.tasks.generate_daily_reports',
        'schedule': crontab(hour=0, minute=30),  # 12:30 AM daily
    },
    'gst-filing-reminder': {
        'task': 'apps.accounting.tasks.gst_filing_reminder',
        'schedule': crontab(day_of_month=1, hour=9, minute=0),  # 1st of month, 9 AM
    },
    
    # Compliance tasks
    'pdpa-data-retention-cleanup': {
        'task': 'apps.compliance.tasks.pdpa_data_retention_cleanup',
        'schedule': crontab(hour=3, minute=0),  # 3 AM daily
    },
}

# =============================================================================
# TASK ANNOTATIONS
# =============================================================================

app.conf.task_annotations = {
    '*': {
        'rate_limit': '100/s',  # Default rate limit
    },
    'apps.payments.tasks.*': {
        'rate_limit': '10/s',  # Lower rate for payment tasks
        'max_retries': 3,
    },
}

# =============================================================================
# DEBUG TASK
# =============================================================================

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to verify Celery is working."""
    print(f'Request: {self.request!r}')

```

# backend/config/urls.py
```py
"""
URL configuration for Singapore SMB E-commerce Platform.

The `urlpatterns` list routes URLs to views.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


def health_check(request):
    """Health check endpoint for load balancers and monitoring."""
    return JsonResponse({
        'status': 'ok',
        'version': settings.PLATFORM_VERSION,
    })


urlpatterns = [
    # Health check (no auth required)
    path('health/', health_check, name='health-check'),
    
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/', include([
        path('accounts/', include('apps.accounts.urls', namespace='accounts')),
        # Future API endpoints:
        # path('commerce/', include('apps.commerce.urls', namespace='commerce')),
        # path('inventory/', include('apps.inventory.urls', namespace='inventory')),
        # path('accounting/', include('apps.accounting.urls', namespace='accounting')),
        # path('compliance/', include('apps.compliance.urls', namespace='compliance')),
        # path('payments/', include('apps.payments.urls', namespace='payments')),
    ])),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Debug toolbar URLs (development only)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

```

