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
