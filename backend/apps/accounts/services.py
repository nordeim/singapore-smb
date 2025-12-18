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
