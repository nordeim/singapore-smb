"""
Payment model for tracking payments.

Supports:
- Multiple payment methods (cash, card, bank, PayNow)
- Gateway integration (Stripe, HitPay)
- Status tracking (pending, completed, failed, refunded)
- Reference to order or invoice
"""
import uuid
from decimal import Decimal

from django.db import models
from django.utils import timezone

from core.models import AuditableModel


# Payment status choices
PAYMENT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
    ('refunded', 'Refunded'),
]

# Payment method choices
PAYMENT_METHOD_CHOICES = [
    ('cash', 'Cash'),
    ('bank_transfer', 'Bank Transfer'),
    ('credit_card', 'Credit Card'),
    ('debit_card', 'Debit Card'),
    ('paynow', 'PayNow'),
    ('cheque', 'Cheque'),
    ('other', 'Other'),
]

# Payment gateway choices
PAYMENT_GATEWAY_CHOICES = [
    ('stripe', 'Stripe'),
    ('hitpay', 'HitPay'),
    ('paynow', 'PayNow Corporate'),
    ('manual', 'Manual'),
]

# Reference type choices
PAYMENT_REFERENCE_TYPE_CHOICES = [
    ('order', 'Order'),
    ('invoice', 'Invoice'),
]


class Payment(AuditableModel):
    """
    Payment record for customer transactions.
    
    Tracks payment method, gateway integration details,
    and status through completion/failure/refund.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    company = models.ForeignKey(
        'accounts.Company',
        on_delete=models.CASCADE,
        related_name='payments',
    )
    
    # Payment identification
    payment_number = models.CharField(
        max_length=50,
        help_text="Unique payment number (e.g., PAY-2024-00001)",
    )
    
    payment_date = models.DateField()
    
    # Amount
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Payment amount",
    )
    
    currency = models.CharField(
        max_length=3,
        default='SGD',
        help_text="ISO 4217 currency code",
    )
    
    # Payment method
    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHOD_CHOICES,
    )
    
    # Gateway info (for online payments)
    gateway = models.CharField(
        max_length=50,
        choices=PAYMENT_GATEWAY_CHOICES,
        blank=True,
        default='',
    )
    
    gateway_reference = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Payment gateway transaction ID",
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
    )
    
    failed_reason = models.TextField(
        blank=True,
        default='',
        help_text="Reason for payment failure",
    )
    
    # Reference to source document
    reference_type = models.CharField(
        max_length=50,
        choices=PAYMENT_REFERENCE_TYPE_CHOICES,
        blank=True,
        default='',
    )
    
    reference_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="UUID of the order or invoice",
    )
    
    # Metadata (for gateway response, etc.)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional payment data from gateway",
    )
    
    # Refund tracking
    refund_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    
    refunded_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    
    # Completion timestamp
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    
    class Meta:
        db_table = '"accounting"."payments"'
        ordering = ['-payment_date', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'payment_number'],
                name='payment_unique_number_per_company',
            ),
        ]
        indexes = [
            models.Index(fields=['company'], name='payments_company_idx'),
            models.Index(
                fields=['reference_type', 'reference_id'],
                name='payments_reference_idx'
            ),
            models.Index(fields=['status'], name='payments_status_idx'),
        ]
    
    def __str__(self) -> str:
        return f"{self.payment_number} - {self.amount} {self.currency}"
    
    @property
    def is_completed(self) -> bool:
        """Check if payment is completed."""
        return self.status == 'completed'
    
    @property
    def is_refunded(self) -> bool:
        """Check if payment is fully refunded."""
        return self.status == 'refunded'
    
    @property
    def is_partially_refunded(self) -> bool:
        """Check if payment is partially refunded."""
        return (
            self.refund_amount > Decimal('0.00') and
            self.refund_amount < self.amount
        )
    
    @property
    def net_amount(self) -> Decimal:
        """Get net amount after refunds."""
        return self.amount - self.refund_amount
    
    def complete(self) -> None:
        """Mark payment as completed."""
        if self.status != 'pending':
            raise ValueError(f"Cannot complete payment with status '{self.status}'")
        
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])
    
    def fail(self, reason: str = '') -> None:
        """Mark payment as failed."""
        if self.status != 'pending':
            raise ValueError(f"Cannot fail payment with status '{self.status}'")
        
        self.status = 'failed'
        self.failed_reason = reason
        self.save(update_fields=['status', 'failed_reason', 'updated_at'])
    
    def refund(self, amount: Decimal = None) -> None:
        """
        Process refund for payment.
        
        Args:
            amount: Refund amount (default: full amount)
        """
        if self.status != 'completed':
            raise ValueError(f"Cannot refund payment with status '{self.status}'")
        
        refund_amount = amount or self.amount
        
        if refund_amount > self.net_amount:
            raise ValueError(
                f"Refund amount ({refund_amount}) exceeds "
                f"net amount ({self.net_amount})"
            )
        
        self.refund_amount += refund_amount
        self.refunded_at = timezone.now()
        
        if self.refund_amount >= self.amount:
            self.status = 'refunded'
        
        self.save(update_fields=[
            'refund_amount', 'refunded_at', 'status', 'updated_at'
        ])
    
    @classmethod
    def generate_payment_number(cls, company) -> str:
        """Generate unique payment number for company."""
        from django.db.models import Max
        
        year = timezone.now().year
        prefix = f"PAY-{year}-"
        
        last_payment = cls.objects.filter(
            company=company,
            payment_number__startswith=prefix,
        ).aggregate(max_num=Max('payment_number'))
        
        if last_payment['max_num']:
            last_num = int(last_payment['max_num'].split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:05d}"
