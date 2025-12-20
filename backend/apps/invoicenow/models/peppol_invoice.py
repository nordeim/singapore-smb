"""
PEPPOL Invoice model for InvoiceNow integration.

Matches schema: compliance.peppol_invoices
"""
import uuid

from django.db import models
from django.utils import timezone


# PEPPOL invoice status choices
PEPPOL_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('validated', 'Validated'),
    ('signed', 'Signed'),
    ('submitted', 'Submitted'),
    ('acknowledged', 'Acknowledged'),
    ('rejected', 'Rejected'),
]


class PEPPOLInvoice(models.Model):
    """
    PEPPOL e-invoice for InvoiceNow submission.
    
    Extends accounting.Invoice with PEPPOL-specific fields.
    Stores generated UBL XML and submission tracking.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Link to accounting invoice
    invoice = models.OneToOneField(
        'accounting.Invoice',
        on_delete=models.CASCADE,
        related_name='peppol_invoice'
    )
    
    # PEPPOL identifiers
    peppol_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='PEPPOL document ID'
    )
    sender_endpoint = models.CharField(
        max_length=100,
        blank=True,
        help_text='Sender PEPPOL participant ID'
    )
    receiver_endpoint = models.CharField(
        max_length=100,
        blank=True,
        help_text='Receiver PEPPOL participant ID'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=PEPPOL_STATUS_CHOICES,
        default='draft'
    )
    
    # UBL XML document
    xml_document = models.TextField(
        blank=True,
        help_text='Generated UBL 2.1 XML'
    )
    
    # Digital signature
    signature_value = models.TextField(
        blank=True,
        help_text='XMLDSig signature value'
    )
    signature_timestamp = models.DateTimeField(
        null=True,
        blank=True
    )
    
    # Submission tracking
    access_point_provider = models.CharField(
        max_length=100,
        blank=True,
        help_text='Access Point provider used'
    )
    submission_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text='AP submission reference'
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    # Validation
    validation_errors = models.JSONField(
        default=list,
        blank=True
    )
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = '"compliance"."peppol_invoices"'
        verbose_name = 'PEPPOL Invoice'
        verbose_name_plural = 'PEPPOL Invoices'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['invoice']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"PEPPOL: {self.invoice.invoice_number}"
    
    def mark_validated(self) -> None:
        """Mark invoice as validated."""
        if self.status != 'draft':
            raise ValueError("Can only validate draft invoices")
        
        self.status = 'validated'
        self.save(update_fields=['status', 'updated_at'])
    
    def mark_signed(self, signature: str) -> None:
        """Mark invoice as signed."""
        if self.status != 'validated':
            raise ValueError("Can only sign validated invoices")
        
        self.status = 'signed'
        self.signature_value = signature
        self.signature_timestamp = timezone.now()
        self.save(update_fields=[
            'status', 'signature_value', 'signature_timestamp', 'updated_at'
        ])
    
    def mark_submitted(self, provider: str, reference: str) -> None:
        """Mark invoice as submitted."""
        if self.status != 'signed':
            raise ValueError("Can only submit signed invoices")
        
        self.status = 'submitted'
        self.access_point_provider = provider
        self.submission_reference = reference
        self.submitted_at = timezone.now()
        self.save(update_fields=[
            'status', 'access_point_provider', 'submission_reference',
            'submitted_at', 'updated_at'
        ])
        
        # Sync to accounting invoice
        self.invoice.peppol_status = 'submitted'
        self.invoice.peppol_id = self.peppol_id
        self.invoice.peppol_submitted_at = self.submitted_at
        self.invoice.save(update_fields=[
            'peppol_status', 'peppol_id', 'peppol_submitted_at', 'updated_at'
        ])
    
    def mark_acknowledged(self) -> None:
        """Mark invoice as acknowledged by receiver."""
        if self.status != 'submitted':
            raise ValueError("Can only acknowledge submitted invoices")
        
        self.status = 'acknowledged'
        self.save(update_fields=['status', 'updated_at'])
        
        self.invoice.peppol_status = 'acknowledged'
        self.invoice.save(update_fields=['peppol_status', 'updated_at'])
    
    def mark_rejected(self, errors: list) -> None:
        """Mark invoice as rejected."""
        self.status = 'rejected'
        self.validation_errors = errors
        self.save(update_fields=['status', 'validation_errors', 'updated_at'])
        
        self.invoice.peppol_status = 'rejected'
        self.invoice.save(update_fields=['peppol_status', 'updated_at'])
