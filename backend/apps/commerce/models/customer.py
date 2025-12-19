"""
Customer and CustomerAddress models.

Customer model includes:
- Customer types (retail, wholesale, VIP)
- B2B fields (company_uen, credit_limit, payment_terms)
- PDPA consent fields with timestamps
"""
from django.db import models
from decimal import Decimal

from core.models import SoftDeleteModel


# Customer type choices
CUSTOMER_TYPE_CHOICES = [
    ('retail', 'Retail'),
    ('wholesale', 'Wholesale'),
    ('vip', 'VIP'),
]

# Address type choices
ADDRESS_TYPE_CHOICES = [
    ('shipping', 'Shipping'),
    ('billing', 'Billing'),
]


class Customer(SoftDeleteModel):
    """
    E-commerce customer with PDPA compliance fields.
    
    Supports both B2C (retail) and B2B (wholesale) customers.
    Company-scoped with unique email per company.
    
    Attributes:
        company: Company that owns this customer record
        user: Optional link to platform user account
        email: Customer email (unique per company)
        customer_type: retail, wholesale, or vip
        consent_marketing: PDPA explicit opt-in for marketing
        consent_analytics: PDPA opt-out for analytics
    """
    
    company = models.ForeignKey(
        'accounts.Company',
        on_delete=models.CASCADE,
        related_name='customers',
        help_text="Company that owns this customer record"
    )
    
    # Optional link to platform user
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_profiles',
        help_text="Optional linked user account"
    )
    
    # Profile
    email = models.EmailField(
        max_length=255,
        help_text="Customer email address"
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Contact phone number"
    )
    
    first_name = models.CharField(
        max_length=100,
        help_text="Customer first name"
    )
    
    last_name = models.CharField(
        max_length=100,
        help_text="Customer last name"
    )
    
    # Customer type
    customer_type = models.CharField(
        max_length=20,
        choices=CUSTOMER_TYPE_CHOICES,
        default='retail',
        help_text="Customer classification"
    )
    
    # B2B fields
    company_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="B2B customer company name"
    )
    
    company_uen = models.CharField(
        max_length=10,
        blank=True,
        help_text="Singapore UEN for B2B customers"
    )
    
    credit_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Credit limit for B2B customers"
    )
    
    credit_used = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Current credit usage"
    )
    
    payment_terms = models.PositiveIntegerField(
        default=0,
        help_text="Payment terms in days (0 = immediate)"
    )
    
    # PDPA Consent fields
    consent_marketing = models.BooleanField(
        default=False,
        help_text="PDPA: Explicit opt-in for marketing communications"
    )
    
    consent_analytics = models.BooleanField(
        default=True,
        help_text="PDPA: Opt-out consent for analytics"
    )
    
    consent_timestamp = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When consent was recorded"
    )
    
    consent_ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address when consent was given"
    )
    
    data_retention_until = models.DateField(
        null=True,
        blank=True,
        help_text="PDPA: Auto-purge date for customer data"
    )
    
    # Preferences
    preferred_language = models.CharField(
        max_length=5,
        default='en',
        help_text="Preferred communication language"
    )
    
    preferred_currency = models.CharField(
        max_length=3,
        default='SGD',
        help_text="Preferred currency"
    )
    
    # Tags for segmentation
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Customer tags for segmentation"
    )
    
    class Meta:
        db_table = '"commerce"."customers"'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        ordering = ['-created_at']
        unique_together = [('company', 'email')]
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['email']),
            models.Index(fields=['company', 'customer_type']),
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    @property
    def full_name(self) -> str:
        """Get customer's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def available_credit(self) -> Decimal:
        """Calculate remaining credit (credit_limit - credit_used)."""
        return self.credit_limit - self.credit_used
    
    @property
    def is_b2b(self) -> bool:
        """Check if customer is a B2B (wholesale) customer."""
        return self.customer_type == 'wholesale' or bool(self.company_uen)
    
    def has_available_credit(self, amount: Decimal) -> bool:
        """
        Check if customer has enough credit for an order.
        
        Args:
            amount: Order amount to check
            
        Returns:
            True if credit_limit is 0 (no limit) or available_credit >= amount
        """
        if self.credit_limit == 0:
            return True  # No credit limit
        return self.available_credit >= amount


class CustomerAddress(models.Model):
    """
    Customer shipping or billing address.
    
    Follows Singapore address format with postal code and unit number.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=None,
        editable=False
    )
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='addresses',
        help_text="Customer this address belongs to"
    )
    
    address_type = models.CharField(
        max_length=20,
        choices=ADDRESS_TYPE_CHOICES,
        default='shipping',
        help_text="Address type"
    )
    
    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is the default address for its type"
    )
    
    # Recipient
    recipient_name = models.CharField(
        max_length=200,
        help_text="Recipient name"
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Contact phone for delivery"
    )
    
    # Address fields
    address_line1 = models.CharField(
        max_length=255,
        help_text="Street address"
    )
    
    address_line2 = models.CharField(
        max_length=255,
        blank=True,
        help_text="Additional address info"
    )
    
    postal_code = models.CharField(
        max_length=6,
        help_text="Singapore 6-digit postal code"
    )
    
    country = models.CharField(
        max_length=2,
        default='SG',
        help_text="Country code (ISO 3166-1 alpha-2)"
    )
    
    # Singapore-specific
    building_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Building or condo name"
    )
    
    unit_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Unit number (e.g., #01-01)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = '"commerce"."customer_addresses"'
        verbose_name = 'Customer Address'
        verbose_name_plural = 'Customer Addresses'
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['customer']),
        ]
    
    def __str__(self):
        return f"{self.recipient_name} - {self.postal_code}"
    
    def save(self, *args, **kwargs):
        """Generate UUID if not set."""
        if self.id is None:
            import uuid
            self.id = uuid.uuid4()
        super().save(*args, **kwargs)
    
    def get_formatted_address(self) -> str:
        """
        Get address formatted for display or shipping labels.
        
        Returns:
            Multi-line formatted address string
        """
        lines = [self.recipient_name]
        
        if self.unit_number:
            lines.append(f"{self.address_line1} {self.unit_number}")
        else:
            lines.append(self.address_line1)
        
        if self.address_line2:
            lines.append(self.address_line2)
        
        if self.building_name:
            lines.append(self.building_name)
        
        lines.append(f"Singapore {self.postal_code}")
        
        if self.phone:
            lines.append(f"Tel: {self.phone}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        """
        Convert address to dictionary for JSONB storage in orders.
        
        Returns:
            Dict representation of address
        """
        return {
            'recipient_name': self.recipient_name,
            'phone': self.phone,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'postal_code': self.postal_code,
            'country': self.country,
            'building_name': self.building_name,
            'unit_number': self.unit_number,
        }
