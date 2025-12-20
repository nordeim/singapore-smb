"""
Invoice Service for invoice operations.

Provides:
- Invoice creation from orders
- Payment application
- Status management
- Invoice number generation
"""
from decimal import Decimal
from datetime import date, timedelta
from typing import Optional
import logging

from django.db import transaction
from django.utils import timezone

from apps.accounting.models import Invoice
from apps.accounting.gst import GSTEngine


logger = logging.getLogger(__name__)


class InvoiceService:
    """
    Service for managing customer invoices.
    """
    
    # Default payment terms (days)
    DEFAULT_PAYMENT_TERMS_DAYS = 30
    
    @staticmethod
    def create_from_order(
        order,
        payment_terms_days: Optional[int] = None,
    ) -> Invoice:
        """
        Create an invoice from a completed order.
        
        Args:
            order: Order instance
            payment_terms_days: Days until due (default 30)
            
        Returns:
            Created Invoice
        """
        payment_terms = payment_terms_days or InvoiceService.DEFAULT_PAYMENT_TERMS_DAYS
        
        # Generate invoice number
        invoice_number = Invoice.generate_invoice_number(order.company)
        
        # Calculate dates
        invoice_date = date.today()
        due_date = invoice_date + timedelta(days=payment_terms)
        
        # Get amounts from order
        subtotal = order.subtotal
        gst_amount = order.gst_amount
        total_amount = order.total_amount
        
        with transaction.atomic():
            invoice = Invoice.objects.create(
                company=order.company,
                customer=order.customer,
                order_id=order.id,
                invoice_number=invoice_number,
                invoice_date=invoice_date,
                due_date=due_date,
                subtotal=subtotal,
                gst_amount=gst_amount,
                total_amount=total_amount,
                status='draft',
            )
            
            logger.info(f"Created invoice {invoice.invoice_number} from order {order.order_number}")
            
            return invoice
    
    @staticmethod
    def create_manual(
        company,
        customer=None,
        subtotal: Decimal = Decimal('0.00'),
        gst_code: str = 'SR',
        payment_terms_days: int = 30,
        notes: str = '',
        terms: str = '',
    ) -> Invoice:
        """
        Create a manual invoice (not from order).
        
        Args:
            company: Company instance
            customer: Optional Customer instance
            subtotal: Subtotal before GST
            gst_code: GST treatment code
            payment_terms_days: Days until due
            notes: Internal notes
            terms: Payment terms text
            
        Returns:
            Created Invoice
        """
        # Calculate GST
        gst_result = GSTEngine.calculate(subtotal, gst_code)
        
        # Generate invoice number
        invoice_number = Invoice.generate_invoice_number(company)
        
        # Calculate dates
        invoice_date = date.today()
        due_date = invoice_date + timedelta(days=payment_terms_days)
        
        invoice = Invoice.objects.create(
            company=company,
            customer=customer,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            due_date=due_date,
            subtotal=subtotal,
            gst_amount=gst_result.gst_amount,
            total_amount=gst_result.gross_amount,
            status='draft',
            notes=notes,
            terms=terms,
        )
        
        logger.info(f"Created manual invoice {invoice.invoice_number}")
        
        return invoice
    
    @staticmethod
    def apply_payment(
        invoice: Invoice,
        amount: Decimal,
    ) -> None:
        """
        Apply a payment to an invoice.
        
        Args:
            invoice: Invoice to apply payment to
            amount: Payment amount
        """
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        
        if amount > invoice.amount_due:
            raise ValueError(
                f"Payment ({amount}) exceeds amount due ({invoice.amount_due})"
            )
        
        with transaction.atomic():
            invoice.apply_payment(amount)
            logger.info(
                f"Applied payment of {amount} to invoice {invoice.invoice_number}"
            )
    
    @staticmethod
    def mark_sent(invoice: Invoice) -> None:
        """
        Mark invoice as sent to customer.
        
        Args:
            invoice: Invoice to mark as sent
        """
        invoice.mark_sent()
        logger.info(f"Marked invoice {invoice.invoice_number} as sent")
    
    @staticmethod
    def void(invoice: Invoice) -> None:
        """
        Void an invoice.
        
        Args:
            invoice: Invoice to void
        """
        invoice.mark_void()
        logger.info(f"Voided invoice {invoice.invoice_number}")
    
    @staticmethod
    def check_overdue_invoices(company) -> int:
        """
        Check and update overdue status for all sent invoices.
        
        Args:
            company: Company to check
            
        Returns:
            Count of invoices marked overdue
        """
        today = date.today()
        
        overdue_invoices = Invoice.objects.filter(
            company=company,
            status='sent',
            due_date__lt=today,
        )
        
        count = 0
        for invoice in overdue_invoices:
            invoice.status = 'overdue'
            invoice.save(update_fields=['status', 'updated_at'])
            count += 1
        
        if count > 0:
            logger.info(f"Marked {count} invoices as overdue for company {company.id}")
        
        return count
    
    @staticmethod
    def get_aging_summary(company) -> dict:
        """
        Get accounts receivable aging summary.
        
        Returns breakdown by age buckets:
        - Current (not yet due)
        - 1-30 days overdue
        - 31-60 days overdue
        - 61-90 days overdue
        - 90+ days overdue
        
        Args:
            company: Company to analyze
            
        Returns:
            Dict with aging buckets and totals
        """
        today = date.today()
        
        # Get unpaid invoices
        invoices = Invoice.objects.filter(
            company=company,
            status__in=['sent', 'overdue'],
        )
        
        buckets = {
            'current': Decimal('0.00'),
            '1_30': Decimal('0.00'),
            '31_60': Decimal('0.00'),
            '61_90': Decimal('0.00'),
            '90_plus': Decimal('0.00'),
        }
        
        for invoice in invoices:
            amount_due = invoice.amount_due
            days_overdue = (today - invoice.due_date).days
            
            if days_overdue <= 0:
                buckets['current'] += amount_due
            elif days_overdue <= 30:
                buckets['1_30'] += amount_due
            elif days_overdue <= 60:
                buckets['31_60'] += amount_due
            elif days_overdue <= 90:
                buckets['61_90'] += amount_due
            else:
                buckets['90_plus'] += amount_due
        
        buckets['total'] = sum(buckets.values())
        
        return buckets
