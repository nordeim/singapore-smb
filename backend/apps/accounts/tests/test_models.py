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
