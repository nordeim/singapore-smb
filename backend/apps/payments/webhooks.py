"""
Payment webhook handlers.

CSRF-exempt views for processing gateway webhooks.
"""
import logging

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.payments.gateways import StripeAdapter, HitPayAdapter
from apps.payments.services import PaymentOrchestrator
from apps.payments.exceptions import WebhookVerificationError


logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """
    Handle Stripe webhooks.
    
    POST /api/v1/payments/webhooks/stripe/
    """
    
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        payload = request.body
        signature = request.META.get('HTTP_STRIPE_SIGNATURE', '')
        
        adapter = StripeAdapter()
        
        try:
            # Verify signature
            adapter.verify_webhook(payload, signature)
            
            # Parse event
            event = adapter.parse_webhook_event(payload)
            
            logger.info(f"Stripe webhook: {event.get('event_type')}")
            
            # Handle events
            event_type = event.get('event_type', '')
            
            if event_type == 'payment_intent.succeeded':
                PaymentOrchestrator.handle_payment_success(
                    gateway='stripe',
                    payment_intent_id=event.get('payment_intent_id'),
                    metadata=event.get('metadata', {}),
                )
            elif event_type == 'payment_intent.payment_failed':
                PaymentOrchestrator.handle_payment_failure(
                    gateway='stripe',
                    payment_intent_id=event.get('payment_intent_id'),
                    error_message='Payment failed',
                    metadata=event.get('metadata', {}),
                )
            
            return Response({'received': True})
            
        except WebhookVerificationError as e:
            logger.warning(f"Stripe webhook verification failed: {e}")
            return Response(
                {'error': 'Invalid signature'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Stripe webhook error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class HitPayWebhookView(APIView):
    """
    Handle HitPay webhooks.
    
    POST /api/v1/payments/webhooks/hitpay/
    """
    
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        payload = request.body
        
        # HitPay sends HMAC in the payload
        import urllib.parse
        params = urllib.parse.parse_qs(payload.decode('utf-8'))
        signature = params.get('hmac', [''])[0]
        
        adapter = HitPayAdapter()
        
        try:
            # Verify signature
            adapter.verify_webhook(payload, signature)
            
            # Parse event
            event = adapter.parse_webhook_event(payload)
            
            logger.info(f"HitPay webhook: {event.get('event_type')}")
            
            # Handle events
            payment_status = event.get('status', '')
            
            if payment_status == 'completed':
                PaymentOrchestrator.handle_payment_success(
                    gateway='hitpay',
                    payment_intent_id=event.get('payment_request_id'),
                    metadata={
                        'order_id': event.get('reference_number'),
                    },
                )
            elif payment_status in ['failed', 'expired']:
                PaymentOrchestrator.handle_payment_failure(
                    gateway='hitpay',
                    payment_intent_id=event.get('payment_request_id'),
                    error_message=f'Payment {payment_status}',
                    metadata={
                        'order_id': event.get('reference_number'),
                    },
                )
            
            return Response({'received': True})
            
        except WebhookVerificationError as e:
            logger.warning(f"HitPay webhook verification failed: {e}")
            return Response(
                {'error': 'Invalid signature'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"HitPay webhook error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
