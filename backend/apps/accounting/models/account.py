"""
Account model for Chart of Accounts.

Supports hierarchical account structure with types:
- Asset (debit normal)
- Liability (credit normal)
- Equity (credit normal)
- Revenue (credit normal)
- Expense (debit normal)
"""
import uuid
from decimal import Decimal
from typing import List, Optional

from django.db import models
from django.core.validators import RegexValidator

from core.models import AuditableModel


# Account type choices
ACCOUNT_TYPE_CHOICES = [
    ('asset', 'Asset'),
    ('liability', 'Liability'),
    ('equity', 'Equity'),
    ('revenue', 'Revenue'),
    ('expense', 'Expense'),
]

# Account subtype choices (common subtypes per type)
ACCOUNT_SUBTYPE_CHOICES = [
    # Asset subtypes
    ('current', 'Current Asset'),
    ('fixed', 'Fixed Asset'),
    ('intangible', 'Intangible Asset'),
    # Liability subtypes
    ('current_liability', 'Current Liability'),
    ('long_term', 'Long-term Liability'),
    # Equity subtypes
    ('capital', 'Capital'),
    ('retained', 'Retained Earnings'),
    # Revenue subtypes
    ('operating', 'Operating Revenue'),
    ('other_income', 'Other Income'),
    # Expense subtypes
    ('cogs', 'Cost of Goods Sold'),
    ('operating_expense', 'Operating Expense'),
    ('other_expense', 'Other Expense'),
]

# GST code choices
GST_CODE_CHOICES = [
    ('SR', 'Standard Rated'),
    ('ZR', 'Zero Rated'),
    ('ES', 'Exempt Supply'),
    ('OS', 'Out of Scope'),
]


class Account(AuditableModel):
    """
    Chart of Accounts entry.
    
    Supports hierarchical structure via parent_id for sub-accounts.
    Each company has its own chart of accounts.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    company = models.ForeignKey(
        'accounts.Company',
        on_delete=models.CASCADE,
        related_name='accounts',
    )
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        help_text="Parent account for hierarchy",
    )
    
    # Account identification
    code = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^[A-Z0-9\-]+$',
            message="Account code must be alphanumeric with optional hyphens"
        )],
        help_text="Unique account code within company (e.g., 1000, 1100-001)",
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    
    # Classification
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
    )
    
    account_subtype = models.CharField(
        max_length=50,
        choices=ACCOUNT_SUBTYPE_CHOICES,
        blank=True,
        default='',
    )
    
    # GST mapping
    gst_code = models.CharField(
        max_length=2,
        choices=GST_CODE_CHOICES,
        blank=True,
        default='',
        help_text="Default GST treatment for transactions on this account",
    )
    
    # Status flags
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(
        default=False,
        help_text="System accounts cannot be deleted",
    )
    
    # Current balance
    current_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Current account balance (updated when entries are posted)",
    )
    
    class Meta:
        db_table = '"accounting"."accounts"'
        ordering = ['code']
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'code'],
                name='account_unique_code_per_company',
            ),
        ]
        indexes = [
            models.Index(fields=['company'], name='accounts_company_idx'),
            models.Index(fields=['account_type'], name='accounts_type_idx'),
        ]
    
    def __str__(self) -> str:
        return f"{self.code} - {self.name}"
    
    @property
    def is_debit_normal(self) -> bool:
        """
        Returns True if this account type normally has debit balance.
        
        Assets and Expenses are debit-normal.
        Liabilities, Equity, and Revenue are credit-normal.
        """
        return self.account_type in ('asset', 'expense')
    
    @property
    def full_code(self) -> str:
        """Return full hierarchical code including parent codes."""
        if self.parent:
            return f"{self.parent.full_code}.{self.code}"
        return self.code
    
    def get_ancestors(self) -> List['Account']:
        """Get all ancestor accounts (parents up to root)."""
        ancestors = []
        current = self.parent
        while current is not None:
            ancestors.append(current)
            current = current.parent
        return list(reversed(ancestors))
    
    def get_descendants(self) -> List['Account']:
        """Get all descendant accounts (children recursively)."""
        descendants = []
        for child in self.children.all():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants
    
    def get_balance_with_children(self) -> Decimal:
        """Get total balance including all child accounts."""
        total = self.current_balance
        for descendant in self.get_descendants():
            total += descendant.current_balance
        return total
    
    def update_balance(self, amount: Decimal, is_debit: bool) -> None:
        """
        Update account balance based on debit/credit.
        
        For debit-normal accounts (asset/expense):
            - Debit increases balance
            - Credit decreases balance
        
        For credit-normal accounts (liability/equity/revenue):
            - Credit increases balance
            - Debit decreases balance
        """
        if self.is_debit_normal:
            if is_debit:
                self.current_balance += amount
            else:
                self.current_balance -= amount
        else:
            if is_debit:
                self.current_balance -= amount
            else:
                self.current_balance += amount
    
    def clean(self):
        """Validate account data."""
        from django.core.exceptions import ValidationError
        
        # Ensure parent is in same company
        if self.parent and self.parent.company_id != self.company_id:
            raise ValidationError({
                'parent': "Parent account must belong to the same company"
            })
        
        # Prevent circular hierarchy
        if self.parent:
            ancestors = self.get_ancestors()
            if self in ancestors:
                raise ValidationError({
                    'parent': "Circular hierarchy detected"
                })
