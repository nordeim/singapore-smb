"""
Journal Entry model for double-entry accounting.

Each journal entry must be balanced (total debits = total credits).
Entries go through draft -> posted -> (optionally) voided lifecycle.
"""
import uuid
from decimal import Decimal
from typing import List, Tuple

from django.db import models
from django.db.models import Sum
from django.utils import timezone

from core.models import AuditableModel


# Entry status choices
ENTRY_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('posted', 'Posted'),
    ('voided', 'Voided'),
]

# Reference type choices
REFERENCE_TYPE_CHOICES = [
    ('order', 'Order'),
    ('invoice', 'Invoice'),
    ('payment', 'Payment'),
    ('manual', 'Manual Entry'),
    ('adjustment', 'Adjustment'),
]


class JournalEntry(AuditableModel):
    """
    Double-entry accounting journal entry.
    
    Contains header information for the entry.
    Lines are stored in JournalLine model.
    
    Constraint: total_debit must equal total_credit (balanced entry).
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    company = models.ForeignKey(
        'accounts.Company',
        on_delete=models.CASCADE,
        related_name='journal_entries',
    )
    
    # Entry identification
    entry_number = models.CharField(
        max_length=50,
        help_text="Unique entry number within company (e.g., JE-2024-00001)",
    )
    
    entry_date = models.DateField(
        help_text="Date of the transaction",
    )
    
    description = models.TextField(
        blank=True,
        default='',
        help_text="Description of the journal entry",
    )
    
    # Reference to source document
    reference_type = models.CharField(
        max_length=50,
        choices=REFERENCE_TYPE_CHOICES,
        blank=True,
        default='',
    )
    
    reference_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="UUID of the source document (order, invoice, etc.)",
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=ENTRY_STATUS_CHOICES,
        default='draft',
    )
    
    posted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when entry was posted",
    )
    
    # Totals (for validation)
    total_debit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    
    total_credit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    
    # Audit
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_journal_entries',
    )
    
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_journal_entries',
    )
    
    class Meta:
        db_table = '"accounting"."journal_entries"'
        ordering = ['-entry_date', '-created_at']
        verbose_name_plural = 'Journal entries'
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'entry_number'],
                name='journal_entry_unique_number_per_company',
            ),
            models.CheckConstraint(
                condition=models.Q(total_debit=models.F('total_credit')),
                name='balanced_entry',
            ),
        ]
        indexes = [
            models.Index(fields=['company'], name='journals_company_idx'),
            models.Index(fields=['entry_date'], name='journals_date_idx'),
            models.Index(
                fields=['reference_type', 'reference_id'],
                name='journals_reference_idx'
            ),
        ]
    
    def __str__(self) -> str:
        return f"{self.entry_number} ({self.entry_date})"
    
    @property
    def is_balanced(self) -> bool:
        """Check if entry is balanced."""
        return self.total_debit == self.total_credit
    
    @property
    def is_draft(self) -> bool:
        """Check if entry is in draft status."""
        return self.status == 'draft'
    
    @property
    def is_posted(self) -> bool:
        """Check if entry is posted."""
        return self.status == 'posted'
    
    @property
    def is_voided(self) -> bool:
        """Check if entry is voided."""
        return self.status == 'voided'
    
    @property
    def can_edit(self) -> bool:
        """Check if entry can be edited."""
        return self.status == 'draft'
    
    def calculate_totals(self) -> Tuple[Decimal, Decimal]:
        """Calculate totals from lines."""
        totals = self.lines.aggregate(
            total_debit=Sum('debit_amount'),
            total_credit=Sum('credit_amount'),
        )
        return (
            totals['total_debit'] or Decimal('0.00'),
            totals['total_credit'] or Decimal('0.00'),
        )
    
    def update_totals(self) -> None:
        """Update totals from lines and save."""
        self.total_debit, self.total_credit = self.calculate_totals()
        self.save(update_fields=['total_debit', 'total_credit', 'updated_at'])
    
    def post(self, approved_by=None) -> None:
        """
        Post the journal entry.
        
        This will:
        1. Validate balance
        2. Update account balances
        3. Set status to 'posted'
        
        Raises:
            ValueError: If entry is not balanced or already posted
        """
        if self.status != 'draft':
            raise ValueError(f"Cannot post entry with status '{self.status}'")
        
        if not self.is_balanced:
            raise ValueError(
                f"Entry is not balanced: debit={self.total_debit}, "
                f"credit={self.total_credit}"
            )
        
        # Update account balances
        for line in self.lines.select_related('account'):
            if line.debit_amount > 0:
                line.account.update_balance(line.debit_amount, is_debit=True)
            else:
                line.account.update_balance(line.credit_amount, is_debit=False)
            line.account.save(update_fields=['current_balance', 'updated_at'])
        
        self.status = 'posted'
        self.posted_at = timezone.now()
        if approved_by:
            self.approved_by = approved_by
        self.save()
    
    def void(self) -> None:
        """
        Void a posted journal entry.
        
        This will:
        1. Reverse account balance updates
        2. Set status to 'voided'
        
        Raises:
            ValueError: If entry is not posted
        """
        if self.status != 'posted':
            raise ValueError(f"Cannot void entry with status '{self.status}'")
        
        # Reverse account balances
        for line in self.lines.select_related('account'):
            if line.debit_amount > 0:
                # Reverse debit = credit
                line.account.update_balance(line.debit_amount, is_debit=False)
            else:
                # Reverse credit = debit
                line.account.update_balance(line.credit_amount, is_debit=True)
            line.account.save(update_fields=['current_balance', 'updated_at'])
        
        self.status = 'voided'
        self.save()
    
    @classmethod
    def generate_entry_number(cls, company) -> str:
        """Generate unique entry number for company."""
        from django.db.models import Max
        
        year = timezone.now().year
        prefix = f"JE-{year}-"
        
        last_entry = cls.objects.filter(
            company=company,
            entry_number__startswith=prefix,
        ).aggregate(max_num=Max('entry_number'))
        
        if last_entry['max_num']:
            last_num = int(last_entry['max_num'].split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:05d}"
