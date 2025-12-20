"""
Abstract base class for payment gateway adapters.

Provides a common interface for integrating with different payment gateways.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, Dict, Any


@dataclass
class PaymentIntent:
    """
    Payment intent created by a gateway.
    
    Represents a pending payment that the frontend can use
    to complete the payment flow.
    """
    id: str
    client_secret: str
    amount: Decimal
    currency: str
    status: str
    gateway: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Gateway-specific fields
    payment_url: Optional[str] = None  # For redirect-based payments
    qr_code_data: Optional[str] = None  # For PayNow QR


@dataclass
class PaymentResult:
    """
    Result of a payment operation.
    """
    success: bool
    payment_id: str
    gateway_reference: str
    amount: Optional[Decimal] = None
    currency: str = 'SGD'
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PaymentGatewayAdapter(ABC):
    """
    Abstract base class for payment gateway adapters.
    
    Implement this class to add support for a new payment gateway.
    Each adapter should handle:
    - Payment intent creation
    - Payment capture
    - Refunds
    - Webhook verification
    """
    
    # Gateway name identifier
    name: str = 'base'
    
    # Supported payment methods
    supported_methods: list = []
    
    @abstractmethod
    def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        order_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> PaymentIntent:
        """
        Create a payment intent.
        
        Args:
            amount: Payment amount
            currency: Currency code (e.g., 'SGD')
            order_id: Order reference
            metadata: Additional data to attach
            idempotency_key: Key to prevent duplicate charges
            
        Returns:
            PaymentIntent with client secret for frontend
            
        Raises:
            PaymentIntentError: If creation fails
        """
        pass
    
    @abstractmethod
    def capture_payment(
        self,
        payment_intent_id: str,
    ) -> PaymentResult:
        """
        Capture a previously authorized payment.
        
        Args:
            payment_intent_id: Gateway payment intent ID
            
        Returns:
            PaymentResult indicating success/failure
            
        Raises:
            PaymentCaptureError: If capture fails
        """
        pass
    
    @abstractmethod
    def refund_payment(
        self,
        payment_id: str,
        amount: Decimal,
        reason: str = '',
    ) -> PaymentResult:
        """
        Refund a payment.
        
        Args:
            payment_id: Gateway payment ID
            amount: Amount to refund
            reason: Reason for refund
            
        Returns:
            PaymentResult for the refund
            
        Raises:
            PaymentRefundError: If refund fails
        """
        pass
    
    @abstractmethod
    def verify_webhook(
        self,
        payload: bytes,
        signature: str,
    ) -> bool:
        """
        Verify webhook signature.
        
        Args:
            payload: Raw webhook payload bytes
            signature: Signature from webhook header
            
        Returns:
            True if signature is valid
            
        Raises:
            WebhookVerificationError: If verification fails
        """
        pass
    
    def parse_webhook_event(
        self,
        payload: bytes,
    ) -> Dict[str, Any]:
        """
        Parse webhook payload into event data.
        
        Override this for gateway-specific parsing.
        
        Args:
            payload: Raw webhook payload
            
        Returns:
            Parsed event data dict
        """
        import json
        return json.loads(payload)
    
    def get_payment_status(self, payment_id: str) -> str:
        """
        Get current status of a payment.
        
        Args:
            payment_id: Gateway payment ID
            
        Returns:
            Status string
        """
        raise NotImplementedError("Subclass should implement get_payment_status")
