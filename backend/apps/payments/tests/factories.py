"""
Test factories for payments.
"""
import factory
from decimal import Decimal
import uuid


class MockPaymentIntent:
    """Mock payment intent for testing."""
    
    def __init__(
        self,
        id: str = None,
        client_secret: str = 'pi_test_secret',
        amount: Decimal = Decimal('100.00'),
        currency: str = 'SGD',
        status: str = 'requires_payment_method',
        gateway: str = 'stripe',
    ):
        self.id = id or f"pi_{uuid.uuid4().hex[:24]}"
        self.client_secret = client_secret
        self.amount = amount
        self.currency = currency
        self.status = status
        self.gateway = gateway
        self.metadata = {}
        self.payment_url = None


class MockPaymentResult:
    """Mock payment result for testing."""
    
    def __init__(
        self,
        success: bool = True,
        payment_id: str = None,
        gateway_reference: str = None,
        amount: Decimal = Decimal('100.00'),
        error_message: str = None,
    ):
        self.success = success
        self.payment_id = payment_id or f"ch_{uuid.uuid4().hex[:24]}"
        self.gateway_reference = gateway_reference or self.payment_id
        self.amount = amount
        self.currency = 'SGD'
        self.error_message = error_message
        self.metadata = {}
