"""
Payments Celery tasks.
"""
import logging
from celery import shared_task

from django.utils import timezone


logger = logging.getLogger(__name__)


@shared_task
def check_pending_payments():
    """
    Check for stale pending payments.
    
    Runs periodically to identify payments that haven't completed.
    """
    from apps.accounting.models import Payment
    from datetime import timedelta
    
    stale_threshold = timezone.now() - timedelta(hours=24)
    
    stale_payments = Payment.objects.filter(
        status='pending',
        created_at__lt=stale_threshold,
    ).count()
    
    if stale_payments > 0:
        logger.warning(f"{stale_payments} payments pending for 24+ hours")
    
    return {'stale_count': stale_payments}


@shared_task
def sync_payment_status(payment_id: str):
    """
    Sync payment status with gateway.
    
    Useful for reconciliation.
    """
    from apps.accounting.models import Payment
    from apps.payments.services import PaymentOrchestrator
    
    try:
        payment = Payment.objects.get(id=payment_id)
        
        if not payment.gateway or not payment.gateway_reference:
            return {'error': 'No gateway reference'}
        
        gateway = PaymentOrchestrator.get_gateway(payment.gateway)
        status = gateway.get_payment_status(payment.gateway_reference)
        
        logger.info(f"Payment {payment_id} status: {status}")
        
        return {'payment_id': payment_id, 'gateway_status': status}
        
    except Payment.DoesNotExist:
        return {'error': 'Payment not found'}
    except Exception as e:
        logger.error(f"Error syncing payment {payment_id}: {e}")
        return {'error': str(e)}
