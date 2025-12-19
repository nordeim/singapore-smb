"""
Cart and CartItem models.

Implements shopping cart functionality with:
- Guest carts via session_id
- 7-day default expiry
- Cart statuses: active, merged, converted, abandoned
"""
from datetime import timedelta
from decimal import Decimal

from django.db import models
from django.utils import timezone

from core.models import SoftDeleteModel


# Cart status choices
CART_STATUS_CHOICES = [
    ('active', 'Active'),
    ('merged', 'Merged'),
    ('converted', 'Converted'),
    ('abandoned', 'Abandoned'),
]


def default_cart_expiry():
    """Default cart expiry: 7 days from now."""
    return timezone.now() + timedelta(days=7)


class Cart(SoftDeleteModel):
    """
    Shopping cart for customers or guest sessions.
    
    Carts can be linked to either:
    - A Customer (logged-in user)
    - A session_id (guest checkout)
    
    Guest carts can be merged into customer carts on login.
    
    Attributes:
        company: Company this cart belongs to
        customer: Optional linked customer
        session_id: Session ID for guest carts
        status: active, merged, converted, or abandoned
        expires_at: Automatic expiry timestamp
    """
    
    company = models.ForeignKey(
        'accounts.Company',
        on_delete=models.CASCADE,
        related_name='carts',
        help_text="Company this cart belongs to"
    )
    
    customer = models.ForeignKey(
        'commerce.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='carts',
        help_text="Customer who owns this cart"
    )
    
    session_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Session ID for guest carts"
    )
    
    status = models.CharField(
        max_length=20,
        choices=CART_STATUS_CHOICES,
        default='active',
        help_text="Cart status"
    )
    
    expires_at = models.DateTimeField(
        default=default_cart_expiry,
        help_text="When this cart expires"
    )
    
    # Conversion tracking
    converted_order_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="Order ID if cart was converted"
    )
    
    converted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When cart was converted to order"
    )
    
    class Meta:
        db_table = '"commerce"."carts"'
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['customer']),
            models.Index(fields=['session_id']),
            models.Index(fields=['expires_at']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(customer__isnull=False) | models.Q(session_id__isnull=False),
                name='cart_identifier_required',
            ),
        ]
    
    def __str__(self):
        if self.customer:
            return f"Cart for {self.customer.email}"
        return f"Guest Cart ({self.session_id[:8]}...)"
    
    @property
    def is_expired(self) -> bool:
        """Check if cart has expired."""
        return timezone.now() > self.expires_at
    
    @property
    def is_guest(self) -> bool:
        """Check if this is a guest cart."""
        return self.customer is None
    
    @property
    def item_count(self) -> int:
        """Get total number of items (sum of quantities)."""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def unique_item_count(self) -> int:
        """Get number of distinct products in cart."""
        return self.items.count()
    
    def calculate_totals(self) -> dict:
        """
        Calculate cart totals including GST.
        
        Returns:
            Dict with subtotal, gst_amount, total, and item_count
        """
        subtotal = Decimal('0.00')
        gst_amount = Decimal('0.00')
        
        for item in self.items.filter(is_saved_for_later=False):
            line_total = item.line_total
            subtotal += line_total
            
            # Calculate GST based on product's GST code
            if item.product.gst_code == 'SR':
                gst_amount += round(line_total * item.product.gst_rate, 2)
        
        return {
            'subtotal': subtotal,
            'gst_amount': gst_amount,
            'total': subtotal + gst_amount,
            'item_count': self.item_count,
        }
    
    def extend_expiry(self, days: int = 7):
        """
        Extend cart expiry from now.
        
        Args:
            days: Number of days to extend
        """
        self.expires_at = timezone.now() + timedelta(days=days)
        self.save(update_fields=['expires_at', 'updated_at'])
    
    def mark_converted(self, order_id):
        """
        Mark cart as converted to an order.
        
        Args:
            order_id: UUID of the created order
        """
        self.status = 'converted'
        self.converted_order_id = order_id
        self.converted_at = timezone.now()
        self.save(update_fields=['status', 'converted_order_id', 'converted_at', 'updated_at'])


class CartItem(models.Model):
    """
    Individual item in a shopping cart.
    
    Stores the unit_price at time of adding to cart
    to preserve pricing even if product price changes.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=None,
        editable=False
    )
    
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Cart this item belongs to"
    )
    
    product = models.ForeignKey(
        'commerce.Product',
        on_delete=models.PROTECT,
        related_name='cart_items',
        help_text="Product being purchased"
    )
    
    variant = models.ForeignKey(
        'commerce.ProductVariant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cart_items',
        help_text="Optional product variant"
    )
    
    quantity = models.PositiveIntegerField(
        default=1,
        help_text="Quantity of this item"
    )
    
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per unit at time of adding to cart"
    )
    
    is_saved_for_later = models.BooleanField(
        default=False,
        help_text="Item saved for later, not in active cart"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = '"commerce"."cart_items"'
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        ordering = ['created_at']
        unique_together = [('cart', 'product', 'variant')]
        indexes = [
            models.Index(fields=['cart']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name='cart_item_quantity_positive',
            ),
        ]
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    def save(self, *args, **kwargs):
        """Generate UUID if not set."""
        if self.id is None:
            import uuid
            self.id = uuid.uuid4()
        super().save(*args, **kwargs)
    
    @property
    def line_total(self) -> Decimal:
        """Calculate line total (quantity * unit_price)."""
        return self.quantity * self.unit_price
    
    @property
    def effective_price(self) -> Decimal:
        """
        Get effective unit price.
        
        Uses variant price if variant is set, otherwise product base price.
        """
        if self.variant:
            return self.variant.effective_price
        return self.product.base_price
    
    def update_quantity(self, new_quantity: int):
        """
        Update item quantity with validation.
        
        Args:
            new_quantity: New quantity (must be > 0)
            
        Raises:
            ValueError: If quantity <= 0
        """
        if new_quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        self.quantity = new_quantity
        self.save(update_fields=['quantity', 'updated_at'])
