"""
Journal Line model for double-entry accounting.

Each line represents either a debit or credit to an account.
Constraint: Either debit_amount > 0 XOR credit_amount > 0 (one side only).
"""
import uuid
from decimal import Decimal

from django.db import models


class JournalLine(models.Model):
    """
    Individual line item in a journal entry.
    
    Each line debits or credits exactly one account.
    The constraint ensures only one side has a non-zero amount.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    journal_entry = models.ForeignKey(
        'accounting.JournalEntry',
        on_delete=models.CASCADE,
        related_name='lines',
    )
    
    account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.PROTECT,
        related_name='journal_lines',
        help_text="Account to debit or credit",
    )
    
    # Amounts (only one should be non-zero)
    debit_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Amount to debit (must be >= 0)",
    )
    
    credit_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Amount to credit (must be >= 0)",
    )
    
    # GST tracking
    gst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="GST portion of this line (for reporting)",
    )
    
    gst_code = models.CharField(
        max_length=2,
        blank=True,
        default='',
        help_text="GST code for this line",
    )
    
    # Description
    description = models.TextField(
        blank=True,
        default='',
        help_text="Line-specific description",
    )
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = '"accounting"."journal_lines"'
        ordering = ['created_at']
        constraints = [
            # Ensure only one side has amount
            models.CheckConstraint(
                condition=(
                    (models.Q(debit_amount__gt=0) & models.Q(credit_amount=0)) |
                    (models.Q(credit_amount__gt=0) & models.Q(debit_amount=0))
                ),
                name='one_side_only',
            ),
            # Ensure amounts are non-negative
            models.CheckConstraint(
                condition=models.Q(debit_amount__gte=0),
                name='debit_amount_non_negative',
            ),
            models.CheckConstraint(
                condition=models.Q(credit_amount__gte=0),
                name='credit_amount_non_negative',
            ),
        ]
        indexes = [
            models.Index(
                fields=['journal_entry'],
                name='journal_lines_entry_idx'
            ),
            models.Index(
                fields=['account'],
                name='journal_lines_account_idx'
            ),
        ]
    
    def __str__(self) -> str:
        if self.is_debit:
            return f"DR {self.account.code}: {self.debit_amount}"
        return f"CR {self.account.code}: {self.credit_amount}"
    
    @property
    def is_debit(self) -> bool:
        """Check if this is a debit line."""
        return self.debit_amount > 0
    
    @property
    def is_credit(self) -> bool:
        """Check if this is a credit line."""
        return self.credit_amount > 0
    
    @property
    def amount(self) -> Decimal:
        """Get the non-zero amount."""
        return self.debit_amount if self.is_debit else self.credit_amount
    
    @property
    def signed_amount(self) -> Decimal:
        """Get signed amount (positive for debit, negative for credit)."""
        if self.is_debit:
            return self.debit_amount
        return -self.credit_amount
    
    def clean(self):
        """Validate line data."""
        from django.core.exceptions import ValidationError
        
        # Ensure at least one amount is positive
        if self.debit_amount == 0 and self.credit_amount == 0:
            raise ValidationError(
                "Either debit_amount or credit_amount must be greater than 0"
            )
        
        # Ensure only one side has amount (also enforced by DB constraint)
        if self.debit_amount > 0 and self.credit_amount > 0:
            raise ValidationError(
                "Only one of debit_amount or credit_amount can be non-zero"
            )
        
        # Ensure amounts are non-negative
        if self.debit_amount < 0:
            raise ValidationError({'debit_amount': "Amount cannot be negative"})
        if self.credit_amount < 0:
            raise ValidationError({'credit_amount': "Amount cannot be negative"})
    
    def save(self, *args, **kwargs):
        """
        Save the journal line.
        
        Note: Does NOT automatically update parent entry totals.
        The service layer must call entry.update_totals() after all lines
        are created to ensure the balanced_entry constraint is satisfied.
        """
        self.full_clean()
        super().save(*args, **kwargs)

