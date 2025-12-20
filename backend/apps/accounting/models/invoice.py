"""
Invoice model for customer billing.

Supports:
- Draft to paid lifecycle
- GST-compliant invoicing
- PEPPOL/InvoiceNow fields for e-invoicing
- Computed amount_due property
"""
import uuid
from decimal import Decimal
from datetime import date

from django.db import models
from django.utils import timezone

from core.models import AuditableModel


# Invoice status choices
INVOICE_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('sent', 'Sent'),
    ('paid', 'Paid'),
    ('overdue', 'Overdue'),
    ('void', 'Void'),
]

# PEPPOL status choices
PEPPOL_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('submitted', 'Submitted'),
    ('acknowledged', 'Acknowledged'),
    ('rejected', 'Rejected'),
]


class Invoice(AuditableModel):
    """
    Customer invoice for goods or services.
    
    Tracks payment status and supports PEPPOL/InvoiceNow
    for Singapore e-invoicing compliance.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    company = models.ForeignKey(
        'accounts.Company',
        on_delete=models.CASCADE,
        related_name='invoices',
    )
    
    customer = models.ForeignKey(
        'commerce.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        help_text="Customer (optional for cash sales)",
    )
    
    order_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="Reference to source order",
    )
    
    # Invoice identification
    invoice_number = models.CharField(
        max_length=50,
        help_text="Unique invoice number (e.g., INV-2024-00001)",
    )
    
    invoice_date = models.DateField()
    
    due_date = models.DateField(
        help_text="Payment due date",
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=INVOICE_STATUS_CHOICES,
        default='draft',
    )
    
    # Amounts
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Subtotal before GST",
    )
    
    gst_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="GST amount",
    )
    
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Total including GST",
    )
    
    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total amount paid",
    )
    
    # Note: amount_due is a property (PostgreSQL GENERATED column)
    # We use property instead since Django cannot directly write to generated columns
    
    # PEPPOL/InvoiceNow fields
    peppol_id = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="PEPPOL invoice identifier",
    )
    
    peppol_status = models.CharField(
        max_length=20,
        choices=PEPPOL_STATUS_CHOICES,
        blank=True,
        default='',
    )
    
    peppol_submitted_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        default='',
        help_text="Internal notes",
    )
    
    terms = models.TextField(
        blank=True,
        default='',
        help_text="Payment terms and conditions",
    )
    
    class Meta:
        db_table = '"accounting"."invoices"'
        ordering = ['-invoice_date', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'invoice_number'],
                name='invoice_unique_number_per_company',
            ),
        ]
        indexes = [
            models.Index(fields=['company'], name='invoices_company_idx'),
            models.Index(fields=['customer'], name='invoices_customer_idx'),
            models.Index(fields=['status'], name='invoices_status_idx'),
            models.Index(fields=['due_date'], name='invoices_due_date_idx'),
        ]
    
    def __str__(self) -> str:
        return f"{self.invoice_number}"
    
    @property
    def amount_due(self) -> Decimal:
        """
        Calculate amount due (total - paid).
        
        Note: This mirrors the PostgreSQL GENERATED ALWAYS AS column.
        """
        return self.total_amount - self.amount_paid
    
    @property
    def is_paid(self) -> bool:
        """Check if invoice is fully paid."""
        return self.amount_due <= Decimal('0.00')
    
    @property
    def is_overdue(self) -> bool:
        """Check if invoice is past due date and not paid."""
        if self.status in ('paid', 'void'):
            return False
        return date.today() > self.due_date
    
    @property
    def is_partially_paid(self) -> bool:
        """Check if invoice is partially paid."""
        return (
            self.amount_paid > Decimal('0.00') and
            self.amount_paid < self.total_amount
        )
    
    def apply_payment(self, amount: Decimal) -> None:
        """
        Apply a payment to this invoice.
        
        Args:
            amount: Payment amount to apply
        """
        self.amount_paid += amount
        if self.is_paid:
            self.status = 'paid'
        self.save(update_fields=['amount_paid', 'status', 'updated_at'])
    
    def mark_sent(self) -> None:
        """Mark invoice as sent to customer."""
        if self.status == 'draft':
            self.status = 'sent'
            self.save(update_fields=['status', 'updated_at'])
    
    def mark_void(self) -> None:
        """Void the invoice."""
        if self.status not in ('paid',):
            self.status = 'void'
            self.save(update_fields=['status', 'updated_at'])
    
    def check_overdue(self) -> bool:
        """Check and update overdue status if needed."""
        if self.is_overdue and self.status == 'sent':
            self.status = 'overdue'
            self.save(update_fields=['status', 'updated_at'])
            return True
        return False
    
    @classmethod
    def generate_invoice_number(cls, company) -> str:
        """Generate unique invoice number for company."""
        from django.db.models import Max
        
        year = timezone.now().year
        month = timezone.now().month
        prefix = f"INV-{year}{month:02d}-"
        
        last_invoice = cls.objects.filter(
            company=company,
            invoice_number__startswith=prefix,
        ).aggregate(max_num=Max('invoice_number'))
        
        if last_invoice['max_num']:
            last_num = int(last_invoice['max_num'].split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:04d}"
    
    def clean(self):
        """Validate invoice data."""
        from django.core.exceptions import ValidationError
        
        # Ensure due_date is not before invoice_date
        if self.due_date and self.invoice_date:
            if self.due_date < self.invoice_date:
                raise ValidationError({
                    'due_date': "Due date cannot be before invoice date"
                })
        
        # Ensure total_amount matches subtotal + gst
        expected_total = self.subtotal + self.gst_amount
        if self.total_amount != expected_total:
            raise ValidationError({
                'total_amount': (
                    f"Total ({self.total_amount}) must equal "
                    f"subtotal + GST ({expected_total})"
                )
            })
