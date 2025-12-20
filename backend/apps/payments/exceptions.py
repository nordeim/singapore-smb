"""
Payment exceptions.
"""


class PaymentError(Exception):
    """Base exception for payment errors."""
    pass


class PaymentGatewayError(PaymentError):
    """Error communicating with payment gateway."""
    pass


class PaymentIntentError(PaymentError):
    """Error creating payment intent."""
    pass


class PaymentCaptureError(PaymentError):
    """Error capturing payment."""
    pass


class PaymentRefundError(PaymentError):
    """Error processing refund."""
    pass


class WebhookVerificationError(PaymentError):
    """Error verifying webhook signature."""
    pass
