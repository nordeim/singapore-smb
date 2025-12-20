"""
Payment Service for payment operations.

Provides:
- Payment recording
- Payment completion/failure
- Refund processing
- Integration with invoice updates
"""
from decimal import Decimal
from datetime import date
from typing import Optional
import logging

from django.db import transaction
from django.utils import timezone

from apps.accounting.models import Payment, Invoice


logger = logging.getLogger(__name__)


class PaymentService:
    """
    Service for managing payments.
    """
    
    @staticmethod
    def record_payment(
        company,
        amount: Decimal,
        payment_method: str,
        payment_date: Optional[date] = None,
        gateway: str = '',
        gateway_reference: str = '',
        reference_type: str = '',
        reference_id=None,
        metadata: dict = None,
    ) -> Payment:
        """
        Record a new payment.
        
        Args:
            company: Company instance
            amount: Payment amount
            payment_method: Method of payment
            payment_date: Date of payment (default: today)
            gateway: Payment gateway used
            gateway_reference: Gateway transaction ID
            reference_type: Type of related document (order/invoice)
            reference_id: UUID of related document
            metadata: Additional payment data
            
        Returns:
            Created Payment
        """
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        
        # Generate payment number
        payment_number = Payment.generate_payment_number(company)
        
        payment = Payment.objects.create(
            company=company,
            payment_number=payment_number,
            payment_date=payment_date or date.today(),
            amount=amount,
            payment_method=payment_method,
            gateway=gateway,
            gateway_reference=gateway_reference,
            reference_type=reference_type,
            reference_id=reference_id,
            metadata=metadata or {},
            status='pending',
        )
        
        logger.info(f"Recorded payment {payment.payment_number}: {amount}")
        
        return payment
    
    @staticmethod
    def complete_payment(payment: Payment) -> None:
        """
        Mark payment as completed.
        
        If payment is linked to an invoice, applies payment amount.
        
        Args:
            payment: Payment to complete
        """
        with transaction.atomic():
            payment.complete()
            
            # Apply to invoice if linked
            if payment.reference_type == 'invoice' and payment.reference_id:
                try:
                    invoice = Invoice.objects.get(id=payment.reference_id)
                    invoice.apply_payment(payment.amount)
                    logger.info(
                        f"Applied payment {payment.payment_number} to "
                        f"invoice {invoice.invoice_number}"
                    )
                except Invoice.DoesNotExist:
                    logger.warning(
                        f"Invoice {payment.reference_id} not found for "
                        f"payment {payment.payment_number}"
                    )
            
            logger.info(f"Completed payment {payment.payment_number}")
    
    @staticmethod
    def fail_payment(payment: Payment, reason: str = '') -> None:
        """
        Mark payment as failed.
        
        Args:
            payment: Payment to mark as failed
            reason: Reason for failure
        """
        payment.fail(reason)
        logger.info(f"Failed payment {payment.payment_number}: {reason}")
    
    @staticmethod
    def refund_payment(
        payment: Payment,
        amount: Optional[Decimal] = None,
    ) -> None:
        """
        Process a refund for a payment.
        
        Args:
            payment: Payment to refund
            amount: Refund amount (default: full amount)
        """
        with transaction.atomic():
            payment.refund(amount)
            
            # TODO: Reverse invoice payment if applicable
            
            logger.info(
                f"Refunded {amount or payment.amount} from "
                f"payment {payment.payment_number}"
            )
    
    @staticmethod
    def record_and_complete_payment(
        company,
        amount: Decimal,
        payment_method: str,
        invoice: Optional[Invoice] = None,
        gateway: str = '',
        gateway_reference: str = '',
    ) -> Payment:
        """
        Convenience method to record and immediately complete a payment.
        
        Useful for cash/immediate payments.
        
        Args:
            company: Company instance
            amount: Payment amount
            payment_method: Method of payment
            invoice: Optional invoice to apply to
            gateway: Payment gateway
            gateway_reference: Gateway reference
            
        Returns:
            Completed Payment
        """
        with transaction.atomic():
            payment = PaymentService.record_payment(
                company=company,
                amount=amount,
                payment_method=payment_method,
                gateway=gateway,
                gateway_reference=gateway_reference,
                reference_type='invoice' if invoice else '',
                reference_id=invoice.id if invoice else None,
            )
            
            PaymentService.complete_payment(payment)
            
            return payment
    
    @staticmethod
    def get_payments_for_invoice(invoice: Invoice) -> list:
        """
        Get all payments for an invoice.
        
        Args:
            invoice: Invoice to query
            
        Returns:
            List of Payment objects
        """
        return list(Payment.objects.filter(
            reference_type='invoice',
            reference_id=invoice.id,
            status='completed',
        ).order_by('-payment_date'))
    
    @staticmethod
    def get_daily_payments_summary(company, payment_date: date) -> dict:
        """
        Get payment summary for a specific date.
        
        Args:
            company: Company to query
            payment_date: Date to summarize
            
        Returns:
            Dict with totals by payment method
        """
        payments = Payment.objects.filter(
            company=company,
            payment_date=payment_date,
            status='completed',
        )
        
        summary = {
            'total': Decimal('0.00'),
            'by_method': {},
        }
        
        for payment in payments:
            summary['total'] += payment.net_amount
            method = payment.payment_method
            if method not in summary['by_method']:
                summary['by_method'][method] = Decimal('0.00')
            summary['by_method'][method] += payment.net_amount
        
        return summary
