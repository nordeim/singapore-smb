"""
Payment orchestrator service.

Provides:
- Gateway selection based on payment method
- Payment creation and processing
- Integration with Order and Invoice services
"""
import logging
from decimal import Decimal
from typing import Optional, Dict, Any, List
import uuid

from django.db import transaction
from django.conf import settings

from apps.payments.gateways import (
    PaymentGatewayAdapter, PaymentIntent, PaymentResult,
    StripeAdapter, HitPayAdapter,
)
from apps.payments.exceptions import PaymentError, PaymentGatewayError
from apps.accounting.models import Payment


logger = logging.getLogger(__name__)


class PaymentOrchestrator:
    """
    Orchestrates payment processing across multiple gateways.
    
    Features:
    - Gateway selection based on payment method
    - Payment intent creation for frontend
    - Payment recording in accounting
    - Integration with order and invoice services
    """
    
    # Map payment methods to gateways
    PAYMENT_METHOD_GATEWAY = {
        'card': 'stripe',
        'apple_pay': 'stripe',
        'google_pay': 'stripe',
        'paynow': 'hitpay',
        'grabpay': 'hitpay',
        'shopee_pay': 'hitpay',
    }
    
    # Available gateways
    GATEWAYS = {
        'stripe': StripeAdapter,
        'hitpay': HitPayAdapter,
    }
    
    @staticmethod
    def get_available_methods(company=None) -> List[str]:
        """
        Get available payment methods for a company.
        
        Returns methods ordered by priority (Stripe first, then HitPay).
        
        Returns:
            List of available payment method codes
        """
        methods = []
        
        # Get primary gateway from settings (default: stripe)
        primary = getattr(settings, 'PAYMENT_PRIMARY_GATEWAY', 'stripe')
        
        # Check Stripe availability (primary)
        if getattr(settings, 'STRIPE_SECRET_KEY', ''):
            stripe_methods = ['card', 'apple_pay', 'google_pay']
            if primary == 'stripe':
                methods = stripe_methods + methods
            else:
                methods.extend(stripe_methods)
        
        # Check HitPay availability (secondary)
        if getattr(settings, 'HITPAY_API_KEY', ''):
            hitpay_methods = ['paynow', 'grabpay', 'shopee_pay']
            if primary == 'hitpay':
                methods = hitpay_methods + methods
            else:
                methods.extend(hitpay_methods)
        
        return methods
    
    @staticmethod
    def get_default_gateway() -> str:
        """
        Get the default/primary payment gateway.
        
        Returns:
            Gateway name (stripe or hitpay)
        """
        return getattr(settings, 'PAYMENT_PRIMARY_GATEWAY', 'stripe')
    
    @staticmethod
    def get_gateway(gateway_name: str) -> PaymentGatewayAdapter:
        """
        Get a gateway adapter instance.
        
        Args:
            gateway_name: Name of the gateway
            
        Returns:
            Gateway adapter instance
        """
        if gateway_name not in PaymentOrchestrator.GATEWAYS:
            raise PaymentGatewayError(f"Unknown gateway: {gateway_name}")
        
        return PaymentOrchestrator.GATEWAYS[gateway_name]()
    
    @staticmethod
    def get_gateway_for_method(payment_method: str) -> PaymentGatewayAdapter:
        """
        Get the appropriate gateway for a payment method.
        
        Args:
            payment_method: Payment method code
            
        Returns:
            Gateway adapter instance
        """
        gateway_name = PaymentOrchestrator.PAYMENT_METHOD_GATEWAY.get(payment_method)
        
        if not gateway_name:
            raise PaymentGatewayError(f"Unknown payment method: {payment_method}")
        
        return PaymentOrchestrator.get_gateway(gateway_name)
    
    @staticmethod
    def create_payment_intent(
        order,
        payment_method: str,
        redirect_url: str = None,
        webhook_url: str = None,
    ) -> PaymentIntent:
        """
        Create a payment intent for an order.
        
        Args:
            order: Order to create payment for
            payment_method: Payment method code
            redirect_url: URL to redirect after payment (for HitPay)
            webhook_url: URL for payment webhooks
            
        Returns:
            PaymentIntent for frontend
        """
        gateway = PaymentOrchestrator.get_gateway_for_method(payment_method)
        
        intent = gateway.create_payment_intent(
            amount=order.total_amount,
            currency='SGD',
            order_id=str(order.id),
            metadata={
                'order_number': order.order_number,
                'company_id': str(order.company_id),
                'payment_method': payment_method,
            },
            idempotency_key=f"order_{order.id}_{payment_method}",
        )
        
        logger.info(
            f"Created payment intent {intent.id} for order {order.order_number} "
            f"via {gateway.name}"
        )
        
        return intent
    
    @staticmethod
    def process_payment(
        order,
        payment_method: str,
        gateway_reference: str,
    ) -> Payment:
        """
        Record a successful payment.
        
        Called after gateway confirms payment success.
        
        Args:
            order: Order being paid for
            payment_method: Payment method used
            gateway_reference: Gateway's payment ID
            
        Returns:
            Created Payment record
        """
        with transaction.atomic():
            # Create payment record
            payment = Payment.objects.create(
                company=order.company,
                invoice=None,  # Will be linked when invoice is created
                payment_number=Payment.generate_payment_number(order.company),
                payment_date=order.order_date,
                amount=order.total_amount,
                currency='SGD',
                payment_method=payment_method,
                gateway=PaymentOrchestrator.PAYMENT_METHOD_GATEWAY.get(payment_method, ''),
                gateway_reference=gateway_reference,
                status='completed',
            )
            
            # Update order status if applicable
            if hasattr(order, 'mark_paid'):
                order.mark_paid()
            
            logger.info(
                f"Recorded payment {payment.payment_number} for order {order.order_number}"
            )
            
            return payment
    
    @staticmethod
    def handle_payment_success(
        gateway: str,
        payment_intent_id: str,
        metadata: Dict[str, Any],
    ) -> Optional[Payment]:
        """
        Handle successful payment callback.
        
        Called from webhook handlers.
        
        Args:
            gateway: Gateway name
            payment_intent_id: Gateway payment intent ID
            metadata: Payment metadata including order_id
            
        Returns:
            Created Payment or None if already processed
        """
        from apps.commerce.models import Order
        
        order_id = metadata.get('order_id')
        if not order_id:
            logger.warning(f"Payment {payment_intent_id} has no order_id")
            return None
        
        # Check if payment already exists
        existing = Payment.objects.filter(
            gateway_reference=payment_intent_id
        ).first()
        
        if existing:
            logger.info(f"Payment {payment_intent_id} already processed")
            return existing
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            logger.error(f"Order {order_id} not found for payment {payment_intent_id}")
            return None
        
        payment_method = metadata.get('payment_method', 'card')
        
        return PaymentOrchestrator.process_payment(
            order=order,
            payment_method=payment_method,
            gateway_reference=payment_intent_id,
        )
    
    @staticmethod
    def handle_payment_failure(
        gateway: str,
        payment_intent_id: str,
        error_message: str,
        metadata: Dict[str, Any],
    ) -> None:
        """
        Handle failed payment callback.
        
        Args:
            gateway: Gateway name
            payment_intent_id: Gateway payment intent ID
            error_message: Failure reason
            metadata: Payment metadata
        """
        order_id = metadata.get('order_id')
        
        logger.warning(
            f"Payment {payment_intent_id} failed for order {order_id}: {error_message}"
        )
        
        # Could trigger notification to customer here
    
    @staticmethod
    def refund_payment(
        payment: Payment,
        amount: Optional[Decimal] = None,
        reason: str = '',
    ) -> PaymentResult:
        """
        Refund a payment.
        
        Args:
            payment: Payment record to refund
            amount: Amount to refund (None = full refund)
            reason: Refund reason
            
        Returns:
            PaymentResult from gateway
        """
        if not payment.gateway_reference:
            raise PaymentError("Payment has no gateway reference for refund")
        
        refund_amount = amount or payment.amount
        gateway = PaymentOrchestrator.get_gateway(payment.gateway)
        
        result = gateway.refund_payment(
            payment_id=payment.gateway_reference,
            amount=refund_amount,
            reason=reason,
        )
        
        if result.success:
            # Update payment status
            payment.status = 'refunded' if refund_amount == payment.amount else 'partial_refund'
            payment.save(update_fields=['status', 'updated_at'])
            
            logger.info(f"Refunded {refund_amount} for payment {payment.payment_number}")
        
        return result
