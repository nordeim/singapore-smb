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
