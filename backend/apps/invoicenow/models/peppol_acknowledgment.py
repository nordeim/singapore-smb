"""
PEPPOL Acknowledgment model for tracking AP responses.

Matches schema: compliance.peppol_acknowledgments
"""
import uuid

from django.db import models


class PEPPOLAcknowledgment(models.Model):
    """
    PEPPOL message acknowledgment from Access Point.
    
    Tracks delivery receipts and application responses
    from the receiving party.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Link to PEPPOL invoice
    peppol_invoice = models.ForeignKey(
        'invoicenow.PEPPOLInvoice',
        on_delete=models.CASCADE,
        related_name='acknowledgments'
    )
    
    # Acknowledgment type
    ACKNOWLEDGMENT_TYPES = [
        ('delivery', 'Delivery Receipt'),
        ('application', 'Application Response'),
        ('error', 'Error Response'),
    ]
    acknowledgment_type = models.CharField(
        max_length=20,
        choices=ACKNOWLEDGMENT_TYPES
    )
    
    # Response data
    message_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='AP message ID'
    )
    response_code = models.CharField(
        max_length=20,
        blank=True,
        help_text='Response code from receiver'
    )
    response_description = models.TextField(
        blank=True,
        help_text='Response description'
    )
    
    # Full response payload
    response_payload = models.JSONField(
        default=dict,
        blank=True
    )
    
    # Timestamps
    received_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = '"compliance"."peppol_acknowledgments"'
        verbose_name = 'PEPPOL Acknowledgment'
        verbose_name_plural = 'PEPPOL Acknowledgments'
        ordering = ['-received_at']
    
    def __str__(self):
        return f"{self.acknowledgment_type}: {self.peppol_invoice}"
    
    @property
    def is_success(self) -> bool:
        """Check if acknowledgment indicates success."""
        return self.acknowledgment_type != 'error' and self.response_code in ['', 'AP', 'AB']
