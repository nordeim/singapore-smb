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
