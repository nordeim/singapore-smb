"""
Data Access Request model for PDPA compliance.

Matches schema: compliance.data_access_requests
Handles 30-day SLA for access, correction, and deletion requests.
"""
import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone


# Request type choices
REQUEST_TYPE_CHOICES = [
    ('access', 'Data Access'),
    ('correction', 'Data Correction'),
    ('deletion', 'Data Deletion'),
]

# Request status choices
REQUEST_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('completed', 'Completed'),
    ('rejected', 'Rejected'),
]

# PDPA SLA in days
PDPA_SLA_DAYS = 30


class DataAccessRequest(models.Model):
    """
    PDPA data access, correction, or deletion request.
    
    Singapore PDPA requires response within 30 days.
    The due_date is auto-calculated on creation.
    
    Attributes:
        company: Company that received the request
        customer: Customer making the request
        request_type: access, correction, or deletion
        status: Current status of the request
        requested_at: When the request was made
        due_date: Auto-calculated (requested_at + 30 days)
        completed_at: When the request was resolved
        response_notes: Notes on how request was handled
        processed_by: User who handled the request
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    company = models.ForeignKey(
        'accounts.Company',
        on_delete=models.CASCADE,
        related_name='data_access_requests'
    )
    customer = models.ForeignKey(
        'commerce.Customer',
        on_delete=models.CASCADE,
        related_name='data_access_requests'
    )
    
    # Request details
    request_type = models.CharField(
        max_length=20,
        choices=REQUEST_TYPE_CHOICES
    )
    status = models.CharField(
        max_length=20,
        choices=REQUEST_STATUS_CHOICES,
        default='pending'
    )
    
    # Timeline (30-day SLA)
    requested_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateField()
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Response
    response_notes = models.TextField(blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_data_requests'
    )
    
    class Meta:
        db_table = '"compliance"."data_access_requests"'
        verbose_name = 'Data Access Request'
        verbose_name_plural = 'Data Access Requests'
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.get_request_type_display()} request from {self.customer}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate due_date if not set."""
        if not self.due_date:
            self.due_date = (
                self.requested_at.date() + timedelta(days=PDPA_SLA_DAYS)
            )
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self) -> bool:
        """Check if request is past the 30-day SLA."""
        if self.status in ['completed', 'rejected']:
            return False
        return timezone.now().date() > self.due_date
    
    @property
    def days_until_due(self) -> int:
        """Get number of days until due date (negative if overdue)."""
        return (self.due_date - timezone.now().date()).days
    
    @property
    def sla_status(self) -> str:
        """
        Get SLA status for display.
        
        Returns:
            'on_track', 'at_risk' (< 5 days), 'overdue', or 'completed'
        """
        if self.status in ['completed', 'rejected']:
            return 'completed'
        if self.is_overdue:
            return 'overdue'
        if self.days_until_due <= 5:
            return 'at_risk'
        return 'on_track'
    
    def start_processing(self, user) -> None:
        """
        Mark request as being processed.
        
        Args:
            user: User who is handling the request
        """
        if self.status != 'pending':
            raise ValueError("Only pending requests can be started")
        
        self.status = 'processing'
        self.processed_by = user
        self.save(update_fields=['status', 'processed_by', 'updated_at'])
    
    def complete(self, notes: str, user=None) -> None:
        """
        Mark request as completed.
        
        Args:
            notes: Resolution notes
            user: User completing the request
        """
        if self.status not in ['pending', 'processing']:
            raise ValueError("Cannot complete request in current status")
        
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.response_notes = notes
        if user:
            self.processed_by = user
        
        self.save(update_fields=[
            'status', 'completed_at', 'response_notes', 'processed_by', 'updated_at'
        ])
    
    def reject(self, reason: str, user=None) -> None:
        """
        Reject the request with a reason.
        
        Args:
            reason: Rejection reason
            user: User rejecting the request
        """
        if self.status not in ['pending', 'processing']:
            raise ValueError("Cannot reject request in current status")
        
        self.status = 'rejected'
        self.completed_at = timezone.now()
        self.response_notes = reason
        if user:
            self.processed_by = user
        
        self.save(update_fields=[
            'status', 'completed_at', 'response_notes', 'processed_by', 'updated_at'
        ])
