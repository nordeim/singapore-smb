"""
Location model for inventory locations (warehouses, stores).

Implements:
- Location types: warehouse, store, virtual
- Singapore address format
- Company-scoped unique code
"""
from django.db import models

from core.models import SoftDeleteModel


# Location type choices
LOCATION_TYPE_CHOICES = [
    ('warehouse', 'Warehouse'),
    ('store', 'Store'),
    ('virtual', 'Virtual'),
]


class Location(SoftDeleteModel):
    """
    Inventory location (warehouse, store, or virtual).
    
    Locations are company-scoped with unique codes.
    Each location can hold inventory items.
    
    Attributes:
        company: Company that owns this location
        code: Unique code within company (e.g., WH-01, STORE-ORCHARD)
        name: Display name
        location_type: warehouse, store, or virtual
    """
    
    company = models.ForeignKey(
        'accounts.Company',
        on_delete=models.CASCADE,
        related_name='locations',
        help_text="Company that owns this location"
    )
    
    code = models.CharField(
        max_length=20,
        help_text="Unique location code within company"
    )
    
    name = models.CharField(
        max_length=100,
        help_text="Location display name"
    )
    
    location_type = models.CharField(
        max_length=20,
        choices=LOCATION_TYPE_CHOICES,
        default='warehouse',
        help_text="Type of location"
    )
    
    # Address (Singapore format)
    address_line1 = models.CharField(
        max_length=255,
        blank=True,
        help_text="Street address"
    )
    
    address_line2 = models.CharField(
        max_length=255,
        blank=True,
        help_text="Additional address info"
    )
    
    postal_code = models.CharField(
        max_length=6,
        blank=True,
        help_text="Singapore 6-digit postal code"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether location is active"
    )
    
    is_default = models.BooleanField(
        default=False,
        help_text="Default location for new inventory"
    )
    
    # Settings (JSONB for flexibility)
    settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Location-specific settings"
    )
    
    class Meta:
        db_table = '"inventory"."locations"'
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
        ordering = ['code']
        unique_together = [('company', 'code')]
        indexes = [
            models.Index(fields=['company']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def full_address(self) -> str:
        """Get formatted full address."""
        parts = []
        if self.address_line1:
            parts.append(self.address_line1)
        if self.address_line2:
            parts.append(self.address_line2)
        if self.postal_code:
            parts.append(f"Singapore {self.postal_code}")
        return ", ".join(parts) if parts else ""
    
    def save(self, *args, **kwargs):
        """Ensure only one default location per company."""
        if self.is_default:
            # Unset other defaults for this company
            Location.objects.filter(
                company=self.company,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
