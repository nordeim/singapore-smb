"""
Stripe payment gateway adapter.

Supports:
- Card payments
- Apple Pay
- Google Pay
- Stripe PaymentIntents API
"""
import logging
from decimal import Decimal
from typing import Optional, Dict, Any

from django.conf import settings

from apps.payments.gateways.base import PaymentGatewayAdapter, PaymentIntent, PaymentResult
from apps.payments.exceptions import (
    PaymentIntentError, PaymentCaptureError, PaymentRefundError,
    WebhookVerificationError, PaymentGatewayError,
)


logger = logging.getLogger(__name__)


class StripeAdapter(PaymentGatewayAdapter):
    """
    Stripe payment gateway adapter.
    
    Uses Stripe's PaymentIntents API for SCA-ready payments.
    """
    
    name = 'stripe'
    supported_methods = ['card', 'apple_pay', 'google_pay']
    
    def __init__(self):
        """Initialize Stripe client."""
        self._stripe = None
    
    @property
    def stripe(self):
        """Lazy load Stripe module."""
        if self._stripe is None:
            try:
                import stripe
                stripe.api_key = settings.STRIPE_SECRET_KEY
                self._stripe = stripe
            except ImportError:
                raise PaymentGatewayError("stripe package not installed")
        return self._stripe
    
    def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        order_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> PaymentIntent:
        """
        Create a Stripe PaymentIntent.
        
        Args:
            amount: Payment amount
            currency: Currency code (e.g., 'SGD')
            order_id: Order reference
            metadata: Additional data
            idempotency_key: Prevent duplicate charges
            
        Returns:
            PaymentIntent with client_secret
        """
        try:
            # Convert to cents (Stripe uses smallest currency unit)
            amount_cents = int(amount * 100)
            
            intent_data = {
                'amount': amount_cents,
                'currency': currency.lower(),
                'metadata': {
                    'order_id': order_id,
                    **(metadata or {}),
                },
                'automatic_payment_methods': {
                    'enabled': True,
                },
            }
            
            kwargs = {}
            if idempotency_key:
                kwargs['idempotency_key'] = idempotency_key
            
            intent = self.stripe.PaymentIntent.create(**intent_data, **kwargs)
            
            logger.info(f"Created Stripe PaymentIntent {intent.id} for order {order_id}")
            
            return PaymentIntent(
                id=intent.id,
                client_secret=intent.client_secret,
                amount=amount,
                currency=currency,
                status=intent.status,
                gateway=self.name,
                metadata=metadata or {},
            )
            
        except self.stripe.error.StripeError as e:
            logger.error(f"Stripe PaymentIntent error: {e}")
            raise PaymentIntentError(str(e))
    
    def capture_payment(
        self,
        payment_intent_id: str,
    ) -> PaymentResult:
        """
        Capture a Stripe payment.
        
        Note: For automatic capture, this is a no-op as Stripe captures
        automatically when the payment method is confirmed.
        """
        try:
            intent = self.stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == 'requires_capture':
                intent = self.stripe.PaymentIntent.capture(payment_intent_id)
            
            return PaymentResult(
                success=intent.status in ['succeeded', 'processing'],
                payment_id=intent.id,
                gateway_reference=intent.id,
                amount=Decimal(intent.amount) / 100,
                currency=intent.currency.upper(),
            )
            
        except self.stripe.error.StripeError as e:
            logger.error(f"Stripe capture error: {e}")
            raise PaymentCaptureError(str(e))
    
    def refund_payment(
        self,
        payment_id: str,
        amount: Decimal,
        reason: str = '',
    ) -> PaymentResult:
        """
        Refund a Stripe payment.
        
        Supports partial refunds.
        """
        try:
            # Convert to cents
            amount_cents = int(amount * 100)
            
            refund = self.stripe.Refund.create(
                payment_intent=payment_id,
                amount=amount_cents,
                reason='requested_by_customer' if reason else None,
                metadata={'reason_text': reason} if reason else {},
            )
            
            logger.info(f"Created Stripe refund {refund.id} for {amount}")
            
            return PaymentResult(
                success=refund.status == 'succeeded',
                payment_id=refund.id,
                gateway_reference=refund.id,
                amount=Decimal(refund.amount) / 100,
            )
            
        except self.stripe.error.StripeError as e:
            logger.error(f"Stripe refund error: {e}")
            raise PaymentRefundError(str(e))
    
    def verify_webhook(
        self,
        payload: bytes,
        signature: str,
    ) -> bool:
        """
        Verify Stripe webhook signature.
        """
        try:
            webhook_secret = settings.STRIPE_WEBHOOK_SECRET
            
            self.stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            return True
            
        except (ValueError, self.stripe.error.SignatureVerificationError) as e:
            logger.warning(f"Stripe webhook verification failed: {e}")
            raise WebhookVerificationError(str(e))
    
    def parse_webhook_event(
        self,
        payload: bytes,
    ) -> Dict[str, Any]:
        """Parse Stripe webhook payload."""
        import json
        data = json.loads(payload)
        
        return {
            'event_type': data.get('type'),
            'event_id': data.get('id'),
            'payment_intent_id': data.get('data', {}).get('object', {}).get('id'),
            'status': data.get('data', {}).get('object', {}).get('status'),
            'amount': data.get('data', {}).get('object', {}).get('amount'),
            'metadata': data.get('data', {}).get('object', {}).get('metadata', {}),
        }
    
    def get_payment_status(self, payment_id: str) -> str:
        """Get Stripe payment status."""
        try:
            intent = self.stripe.PaymentIntent.retrieve(payment_id)
            return intent.status
        except self.stripe.error.StripeError as e:
            logger.error(f"Error getting payment status: {e}")
            raise PaymentGatewayError(str(e))
