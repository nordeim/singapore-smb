"""
GST Return model for F5 quarterly filing.

Matches schema: compliance.gst_returns
Boxes 1-8 align with IRAS F5 form requirements.
"""
import uuid
from decimal import Decimal

from django.db import models
from django.utils import timezone


# F5 return status choices
GST_RETURN_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('validated', 'Validated'),
    ('submitted', 'Submitted'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
]


class GSTReturn(models.Model):
    """
    GST F5 quarterly return for IRAS filing.
    
    Box values match IRAS GST F5 form:
    - Box 1: Standard-rated supplies
    - Box 2: Zero-rated supplies  
    - Box 3: Exempt supplies
    - Box 4: Total supplies (1+2+3)
    - Box 5: Total taxable purchases
    - Box 6: Output tax due
    - Box 7: Input tax claimable
    - Box 8: Net GST payable/refundable (6-7)
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    company = models.ForeignKey(
        'accounts.Company',
        on_delete=models.CASCADE,
        related_name='gst_returns'
    )
    
    # Period
    period_start = models.DateField()
    period_end = models.DateField()
    quarter = models.IntegerField(
        choices=[(i, f'Q{i}') for i in range(1, 5)]
    )
    year = models.IntegerField()
    
    # F5 Box Values (all DECIMAL(12,2))
    box_1 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Standard-rated supplies'
    )
    box_2 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Zero-rated supplies'
    )
    box_3 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Exempt supplies'
    )
    box_4 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Total supplies (computed: 1+2+3)'
    )
    box_5 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Total taxable purchases'
    )
    box_6 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Output tax due'
    )
    box_7 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Input tax claimable'
    )
    box_8 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Net GST payable/refundable (computed: 6-7)'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=GST_RETURN_STATUS_CHOICES,
        default='draft'
    )
    
    # Submission tracking
    submission_date = models.DateField(null=True, blank=True)
    iras_reference = models.CharField(max_length=100, blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    prepared_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gst_returns_prepared'
    )
    submitted_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gst_returns_submitted'
    )
    
    class Meta:
        db_table = '"compliance"."gst_returns"'
        verbose_name = 'GST Return'
        verbose_name_plural = 'GST Returns'
        ordering = ['-year', '-quarter']
        unique_together = [('company', 'year', 'quarter')]
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"GST F5 Q{self.quarter}/{self.year} - {self.company.name}"
    
    def validate_boxes(self) -> tuple[bool, list[str]]:
        """
        Validate box calculations match expected formulas.
        
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        # Box 4 should equal Box 1 + Box 2 + Box 3
        expected_box_4 = self.box_1 + self.box_2 + self.box_3
        if self.box_4 != expected_box_4:
            errors.append(
                f"Box 4 ({self.box_4}) should equal Box 1+2+3 ({expected_box_4})"
            )
        
        # Box 8 should equal Box 6 - Box 7
        expected_box_8 = self.box_6 - self.box_7
        if self.box_8 != expected_box_8:
            errors.append(
                f"Box 8 ({self.box_8}) should equal Box 6-7 ({expected_box_8})"
            )
        
        return (len(errors) == 0, errors)
    
    def compute_boxes(self) -> None:
        """
        Compute derived box values (Box 4 and Box 8).
        """
        self.box_4 = self.box_1 + self.box_2 + self.box_3
        self.box_8 = self.box_6 - self.box_7
    
    def can_submit(self) -> bool:
        """
        Check if return can be submitted.
        
        Returns:
            True if status is 'validated' and boxes are valid
        """
        if self.status != 'validated':
            return False
        
        is_valid, _ = self.validate_boxes()
        return is_valid
    
    def mark_validated(self) -> None:
        """Mark return as validated after box validation passes."""
        is_valid, errors = self.validate_boxes()
        if not is_valid:
            raise ValueError(f"Cannot validate: {'; '.join(errors)}")
        
        self.status = 'validated'
        self.save(update_fields=['status', 'updated_at'])
    
    def mark_submitted(self, submitted_by, iras_reference: str = '') -> None:
        """
        Mark return as submitted to IRAS.
        
        Args:
            submitted_by: User submitting the return
            iras_reference: IRAS submission reference
        """
        if not self.can_submit():
            raise ValueError("Return must be validated before submission")
        
        self.status = 'submitted'
        self.submission_date = timezone.now().date()
        self.submitted_by = submitted_by
        self.iras_reference = iras_reference
        self.save(update_fields=[
            'status', 'submission_date', 'submitted_by', 'iras_reference', 'updated_at'
        ])
    
    def mark_accepted(self) -> None:
        """Mark return as accepted by IRAS."""
        if self.status != 'submitted':
            raise ValueError("Return must be submitted before acceptance")
        
        self.status = 'accepted'
        self.save(update_fields=['status', 'updated_at'])
    
    def mark_rejected(self, reason: str = '') -> None:
        """Mark return as rejected by IRAS."""
        if self.status != 'submitted':
            raise ValueError("Return must be submitted before rejection")
        
        self.status = 'rejected'
        self.save(update_fields=['status', 'updated_at'])
