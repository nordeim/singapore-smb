"""
Data Consent model for PDPA compliance.

Matches schema: compliance.data_consents
Provides immutable audit trail of consent changes.
"""
import uuid

from django.db import models, transaction
from django.utils import timezone


# Consent type choices (6 types per schema)
CONSENT_TYPE_CHOICES = [
    ('order_processing', 'Order Processing'),
    ('marketing', 'Marketing'),
    ('analytics', 'Analytics'),
    ('third_party', 'Third Party Sharing'),
    ('profiling', 'Profiling'),
    ('legal_compliance', 'Legal Compliance'),
]


class DataConsentManager(models.Manager):
    """Custom manager for DataConsent with consent recording."""
    
    def record_consent(
        self,
        customer,
        consent_type: str,
        is_granted: bool,
        source: str = '',
        ip_address: str = None,
        user_agent: str = '',
    ) -> 'DataConsent':
        """
        Record a consent change and update customer consent fields.
        
        This method:
        1. Creates an immutable consent record
        2. Updates the corresponding Customer consent field
        
        Args:
            customer: Customer giving/withdrawing consent
            consent_type: Type of consent
            is_granted: True if consent given, False if withdrawn
            source: Where consent was recorded (registration, checkout, settings)
            ip_address: Request IP address
            user_agent: Browser user agent
            
        Returns:
            Created DataConsent record
        """
        with transaction.atomic():
            # Create consent record
            consent = self.create(
                customer=customer,
                consent_type=consent_type,
                is_granted=is_granted,
                source=source,
                ip_address=ip_address,
                user_agent=user_agent,
                consent_timestamp=timezone.now(),
            )
            
            # Update customer's consent field
            timestamp = timezone.now() if is_granted else None
            if consent_type == 'marketing':
                customer.consent_marketing = is_granted
                customer.consent_marketing_at = timestamp
            elif consent_type == 'analytics':
                customer.consent_analytics = is_granted
                customer.consent_analytics_at = timestamp
            
            customer.save(update_fields=[
                'consent_marketing', 'consent_marketing_at',
                'consent_analytics', 'consent_analytics_at',
                'updated_at'
            ])
            
            return consent


class DataConsent(models.Model):
    """
    PDPA consent audit record.
    
    This is an IMMUTABLE audit trail of consent changes.
    The current consent state is stored on the Customer model.
    When consent changes, a new record is created here.
    
    Attributes:
        customer: Customer who gave consent
        consent_type: One of 6 consent types
        is_granted: Whether consent was given (True) or withdrawn (False)
        source: Where consent was recorded (e.g., 'registration', 'checkout')
        ip_address: IP address of the request
        user_agent: Browser user agent string
        consent_timestamp: When consent was recorded
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    customer = models.ForeignKey(
        'commerce.Customer',
        on_delete=models.CASCADE,
        related_name='consent_records'
    )
    
    # Consent details
    consent_type = models.CharField(
        max_length=50,
        choices=CONSENT_TYPE_CHOICES
    )
    is_granted = models.BooleanField()
    
    # Context
    source = models.CharField(
        max_length=50,
        blank=True,
        help_text='Where consent was recorded (registration, checkout, settings)'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Timestamp
    consent_timestamp = models.DateTimeField()
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = DataConsentManager()
    
    class Meta:
        db_table = '"compliance"."data_consents"'
        verbose_name = 'Data Consent'
        verbose_name_plural = 'Data Consents'
        ordering = ['-consent_timestamp']
        indexes = [
            models.Index(fields=['customer']),
        ]
    
    def __str__(self):
        action = "granted" if self.is_granted else "withdrew"
        return f"{self.customer} {action} {self.consent_type} consent"
    
    def save(self, *args, **kwargs):
        """
        Override save to enforce immutability.
        
        Consent records cannot be updated once created.
        """
        if self.pk:
            # Check if this is an existing record
            try:
                existing = DataConsent.objects.get(pk=self.pk)
                if existing:
                    raise ValueError(
                        "DataConsent records are immutable and cannot be updated"
                    )
            except DataConsent.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """
        Override delete to prevent deletion.
        
        Consent records must be retained for compliance.
        """
        raise ValueError(
            "DataConsent records cannot be deleted for compliance purposes"
        )
