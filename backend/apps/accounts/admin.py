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
    fk_name = 'user'
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
    list_filter = ['is_active', 'is_verified', 'mfa_enabled', 'company']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']
    filter_horizontal = ()
    
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
            'fields': ('is_active', 'is_superuser', 'is_verified')
        }),
        ('Security', {
            'fields': ('mfa_enabled', 'failed_login_attempts', 'locked_until'),
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
    
    readonly_fields = ['last_login', 'created_at', 'updated_at']
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
