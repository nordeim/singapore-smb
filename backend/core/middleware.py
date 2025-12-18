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
