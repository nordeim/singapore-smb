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
