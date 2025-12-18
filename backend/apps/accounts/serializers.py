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
