"""
InventoryItem model for stock tracking.

Implements:
- Stock quantities (available, reserved, net)
- Optimistic locking with version field
- Reorder point tracking
- net_qty computed as property (DB-generated column is read-only)
"""
from decimal import Decimal

from django.db import models
from django.utils import timezone

from core.models import BaseModel


class InventoryItem(BaseModel):
    """
    Inventory stock record for a product at a location.
    
    Tracks available and reserved quantities with computed net.
    Uses version field for optimistic locking in concurrent operations.
    
    Invariant: reserved_qty <= available_qty (enforced via constraint)
    
    Attributes:
        product: The product this inventory is for
        variant: Optional variant
        location: Where the stock is located
        available_qty: Total quantity in stock
        reserved_qty: Quantity reserved for pending orders
        version: Optimistic lock version number
    """
    
    company = models.ForeignKey(
        'accounts.Company',
        on_delete=models.CASCADE,
        related_name='inventory_items',
        help_text="Company that owns this inventory"
    )
    
    product = models.ForeignKey(
        'commerce.Product',
        on_delete=models.CASCADE,
        related_name='inventory_items',
        help_text="Product this inventory is for"
    )
    
    variant = models.ForeignKey(
        'commerce.ProductVariant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='inventory_items',
        help_text="Optional product variant"
    )
    
    location = models.ForeignKey(
        'inventory.Location',
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Location where stock is held"
    )
    
    # Quantities
    available_qty = models.PositiveIntegerField(
        default=0,
        help_text="Total available quantity"
    )
    
    reserved_qty = models.PositiveIntegerField(
        default=0,
        help_text="Quantity reserved for orders"
    )
    
    # Note: net_qty is GENERATED ALWAYS AS in PostgreSQL
    # We expose it as a property since Django cannot write to it
    
    # Reorder settings
    reorder_point = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Quantity threshold for reorder alert"
    )
    
    reorder_quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Quantity to reorder when low"
    )
    
    # Costing
    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Unit cost for this inventory"
    )
    
    # Tracking timestamps
    last_counted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When last physical count was done"
    )
    
    last_movement_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When last stock movement occurred"
    )
    
    # Optimistic locking
    version = models.PositiveIntegerField(
        default=1,
        help_text="Version for optimistic locking"
    )
    
    class Meta:
        db_table = '"inventory"."items"'
        verbose_name = 'Inventory Item'
        verbose_name_plural = 'Inventory Items'
        ordering = ['product__name', 'location__code']
        unique_together = [('product', 'variant', 'location')]
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['product']),
            models.Index(fields=['location']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(reserved_qty__lte=models.F('available_qty')),
                name='inventory_valid_reserved',
            ),
        ]
    
    def __str__(self):
        if self.variant:
            return f"{self.product.name} ({self.variant.sku}) @ {self.location.code}"
        return f"{self.product.name} @ {self.location.code}"
    
    @property
    def net_qty(self) -> int:
        """
        Calculate net available quantity.
        
        This mirrors the PostgreSQL GENERATED column:
        net_qty = available_qty - reserved_qty
        """
        return self.available_qty - self.reserved_qty
    
    @property
    def is_low_stock(self) -> bool:
        """
        Check if stock is below reorder point.
        
        Uses reorder_point if set, otherwise falls back to
        product.low_stock_threshold.
        """
        threshold = self.reorder_point
        if threshold is None and self.product:
            threshold = self.product.low_stock_threshold
        if threshold is None:
            return False
        return self.net_qty < threshold
    
    @property
    def sku(self) -> str:
        """Get the SKU for this inventory item."""
        if self.variant:
            return self.variant.sku
        return self.product.sku
    
    def increment_version(self):
        """Increment version for optimistic locking."""
        self.version += 1
    
    def update_movement_timestamp(self):
        """Update last_movement_at to now."""
        self.last_movement_at = timezone.now()
    
    def can_reserve(self, quantity: int) -> bool:
        """
        Check if quantity can be reserved.
        
        Args:
            quantity: Amount to reserve
            
        Returns:
            True if net_qty >= quantity
        """
        return self.net_qty >= quantity
