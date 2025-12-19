"""
InventoryReservation model for order reservations.

Implements:
- Stock reservations for pending orders
- Configurable expiry (default 30 minutes)
- Status tracking: pending, confirmed, released, expired
"""
from datetime import timedelta

from django.db import models
from django.conf import settings
from django.utils import timezone


# Reservation status choices
RESERVATION_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('released', 'Released'),
    ('expired', 'Expired'),
]

# Default reservation expiry in minutes (configurable via settings)
DEFAULT_RESERVATION_EXPIRY_MINUTES = getattr(
    settings, 'INVENTORY_RESERVATION_EXPIRY_MINUTES', 30
)


def default_reservation_expiry():
    """Default expiry: 30 minutes from now (configurable)."""
    return timezone.now() + timedelta(minutes=DEFAULT_RESERVATION_EXPIRY_MINUTES)


class InventoryReservation(models.Model):
    """
    Inventory reservation for a pending order.
    
    Reservations hold stock for orders during checkout.
    They expire automatically if not confirmed.
    
    Lifecycle:
    - pending: Created during checkout, stock is reserved
    - confirmed: Order confirmed, reservation finalized
    - released: Order cancelled, stock returned
    - expired: Timeout, stock automatically returned
    
    Attributes:
        inventory_item: The inventory item being reserved
        order_id: UUID of the order (FK added when orders support it)
        quantity: Amount reserved
        status: Current reservation status
        expires_at: When the reservation expires
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=None,
        editable=False
    )
    
    inventory_item = models.ForeignKey(
        'inventory.InventoryItem',
        on_delete=models.CASCADE,
        related_name='reservations',
        help_text="Inventory item being reserved"
    )
    
    order_id = models.UUIDField(
        help_text="Order this reservation is for"
    )
    
    quantity = models.PositiveIntegerField(
        help_text="Quantity reserved"
    )
    
    status = models.CharField(
        max_length=20,
        choices=RESERVATION_STATUS_CHOICES,
        default='pending',
        help_text="Reservation status"
    )
    
    expires_at = models.DateTimeField(
        default=default_reservation_expiry,
        help_text="When this reservation expires"
    )
    
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When reservation was confirmed"
    )
    
    released_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When reservation was released"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = '"inventory"."reservations"'
        verbose_name = 'Inventory Reservation'
        verbose_name_plural = 'Inventory Reservations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['inventory_item']),
            models.Index(fields=['order_id']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name='reservation_quantity_positive',
            ),
        ]
    
    def __str__(self):
        return f"Reservation {self.id} - {self.quantity}x {self.inventory_item}"
    
    def save(self, *args, **kwargs):
        """Generate UUID if not set."""
        if self.id is None:
            import uuid
            self.id = uuid.uuid4()
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self) -> bool:
        """Check if reservation has expired."""
        if self.status != 'pending':
            return False
        return timezone.now() > self.expires_at
    
    @property
    def is_active(self) -> bool:
        """Check if reservation is still active (pending and not expired)."""
        return self.status == 'pending' and not self.is_expired
    
    def confirm(self):
        """
        Confirm the reservation.
        
        Raises:
            ValueError: If not in pending status
        """
        if self.status != 'pending':
            raise ValueError(f"Cannot confirm reservation in {self.status} status")
        self.status = 'confirmed'
        self.confirmed_at = timezone.now()
        self.save(update_fields=['status', 'confirmed_at'])
    
    def release(self):
        """
        Release the reservation.
        
        This should also restore the reserved_qty on the inventory item.
        Typically called via InventoryService.release_reservation().
        """
        if self.status in ['released', 'expired']:
            return  # Already released/expired
        
        self.status = 'released'
        self.released_at = timezone.now()
        self.save(update_fields=['status', 'released_at'])
    
    def expire(self):
        """
        Mark the reservation as expired.
        
        Typically called by cleanup task.
        """
        if self.status != 'pending':
            return
        
        self.status = 'expired'
        self.released_at = timezone.now()
        self.save(update_fields=['status', 'released_at'])
