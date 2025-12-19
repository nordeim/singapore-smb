"""
InventoryMovement model for audit trail.

Implements:
- 8 movement types: purchase, sale, adjustment, transfer_in/out, return, damage, count
- Quantity before/after for audit
- Reference linking to orders, transfers, etc.
- Immutable (append-only audit log)
"""
from django.db import models


# Movement type choices
MOVEMENT_TYPE_CHOICES = [
    ('purchase', 'Purchase'),
    ('sale', 'Sale'),
    ('adjustment', 'Adjustment'),
    ('transfer_in', 'Transfer In'),
    ('transfer_out', 'Transfer Out'),
    ('return', 'Return'),
    ('damage', 'Damage'),
    ('count', 'Count'),
]


class InventoryMovement(models.Model):
    """
    Inventory movement audit log.
    
    Records all stock changes for traceability.
    This is an immutable audit log - no updates or deletes.
    
    Movement types:
    - purchase: Stock received from supplier
    - sale: Stock sold to customer
    - adjustment: Manual correction
    - transfer_in: Received from another location
    - transfer_out: Sent to another location
    - return: Customer return
    - damage: Damaged/written off
    - count: Physical count adjustment
    
    Attributes:
        inventory_item: The item affected
        movement_type: Type of movement
        quantity: Change amount (+/-)
        quantity_before: Stock level before movement
        quantity_after: Stock level after movement
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=None,
        editable=False
    )
    
    company = models.ForeignKey(
        'accounts.Company',
        on_delete=models.CASCADE,
        related_name='inventory_movements',
        help_text="Company that owns this movement"
    )
    
    inventory_item = models.ForeignKey(
        'inventory.InventoryItem',
        on_delete=models.CASCADE,
        related_name='movements',
        help_text="Inventory item affected"
    )
    
    movement_type = models.CharField(
        max_length=30,
        choices=MOVEMENT_TYPE_CHOICES,
        help_text="Type of stock movement"
    )
    
    # Quantity change (positive for in, negative for out)
    quantity = models.IntegerField(
        help_text="Quantity change (+in, -out)"
    )
    
    # Audit trail
    quantity_before = models.IntegerField(
        help_text="Available qty before movement"
    )
    
    quantity_after = models.IntegerField(
        help_text="Available qty after movement"
    )
    
    # Reference to source document
    reference_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Type of reference (order, transfer, etc.)"
    )
    
    reference_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="ID of referenced document"
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this movement"
    )
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_movements',
        help_text="User who created this movement"
    )
    
    class Meta:
        db_table = '"inventory"."movements"'
        verbose_name = 'Inventory Movement'
        verbose_name_plural = 'Inventory Movements'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['inventory_item']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        sign = '+' if self.quantity > 0 else ''
        return f"{self.movement_type}: {sign}{self.quantity} ({self.inventory_item})"
    
    def save(self, *args, **kwargs):
        """Generate UUID if not set. Prevent updates."""
        if self.id is None:
            import uuid
            self.id = uuid.uuid4()
        elif self.pk and InventoryMovement.objects.filter(pk=self.pk).exists():
            # Prevent updates to existing movements
            raise ValueError("InventoryMovement records are immutable")
        super().save(*args, **kwargs)
    
    @classmethod
    def create_movement(
        cls,
        inventory_item,
        movement_type: str,
        quantity: int,
        notes: str = '',
        reference_type: str = '',
        reference_id=None,
        user=None
    ) -> 'InventoryMovement':
        """
        Factory method to create a movement with proper audit trail.
        
        Args:
            inventory_item: InventoryItem instance
            movement_type: Type of movement
            quantity: Change amount (+/-)
            notes: Optional notes
            reference_type: Optional reference type
            reference_id: Optional reference UUID
            user: User creating the movement
            
        Returns:
            Created InventoryMovement instance
        """
        return cls.objects.create(
            company=inventory_item.company,
            inventory_item=inventory_item,
            movement_type=movement_type,
            quantity=quantity,
            quantity_before=inventory_item.available_qty,
            quantity_after=inventory_item.available_qty + quantity,
            reference_type=reference_type,
            reference_id=reference_id,
            notes=notes,
            created_by=user,
        )
