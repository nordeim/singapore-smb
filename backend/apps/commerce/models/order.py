"""
Order and OrderItem models.

Order implements:
- Status state machine: pending → confirmed → processing → shipped → delivered
- Payment status tracking
- GST reporting fields (box_1, box_6) for IRAS F5
- JSONB for shipping/billing addresses
- Order number generation via core.sequences
"""
from decimal import Decimal

from django.db import models
from django.utils import timezone

from core.models import SoftDeleteModel


# Order status choices matching schema
ORDER_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('processing', 'Processing'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
    ('refunded', 'Refunded'),
]

# Payment status choices
PAYMENT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('authorized', 'Authorized'),
    ('paid', 'Paid'),
    ('partially_refunded', 'Partially Refunded'),
    ('refunded', 'Refunded'),
    ('failed', 'Failed'),
]

# Fulfillment status choices
FULFILLMENT_STATUS_CHOICES = [
    ('unfulfilled', 'Unfulfilled'),
    ('partially_fulfilled', 'Partially Fulfilled'),
    ('fulfilled', 'Fulfilled'),
    ('returned', 'Returned'),
]

# Valid status transitions
VALID_STATUS_TRANSITIONS = {
    'pending': ['confirmed', 'cancelled'],
    'confirmed': ['processing', 'cancelled'],
    'processing': ['shipped', 'cancelled'],
    'shipped': ['delivered', 'returned'],
    'delivered': ['refunded'],
    'cancelled': [],
    'refunded': [],
}


class Order(SoftDeleteModel):
    """
    E-commerce order with status state machine and GST tracking.
    
    All monetary fields use DECIMAL(12,2) for financial precision.
    Addresses stored as JSONB snapshots from customer addresses.
    
    Note: The database table is partitioned by order_date,
    but Django ORM treats it as a regular table.
    
    Attributes:
        order_number: Unique order identifier (generated)
        status: Order lifecycle status
        payment_status: Payment processing status
        fulfillment_status: Shipping/fulfillment status
        gst_box_1_amount: Standard-rated supplies for F5
        gst_box_6_amount: Output tax for F5
    """
    
    company = models.ForeignKey(
        'accounts.Company',
        on_delete=models.CASCADE,
        related_name='orders',
        help_text="Company that owns this order"
    )
    
    customer = models.ForeignKey(
        'commerce.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        help_text="Customer who placed this order"
    )
    
    # Order identification
    order_number = models.CharField(
        max_length=50,
        help_text="Unique order number"
    )
    
    # Status fields
    status = models.CharField(
        max_length=30,
        choices=ORDER_STATUS_CHOICES,
        default='pending',
        help_text="Order lifecycle status"
    )
    
    payment_status = models.CharField(
        max_length=30,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        help_text="Payment processing status"
    )
    
    fulfillment_status = models.CharField(
        max_length=30,
        choices=FULFILLMENT_STATUS_CHOICES,
        default='unfulfilled',
        help_text="Fulfillment/shipping status"
    )
    
    # Pricing (DECIMAL precision critical)
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Order subtotal before discounts and shipping"
    )
    
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total discount amount"
    )
    
    shipping_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Shipping cost"
    )
    
    gst_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Total GST amount"
    )
    
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Final order total including GST"
    )
    
    # GST Reporting fields for IRAS F5
    gst_box_1_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Box 1: Standard-rated supplies"
    )
    
    gst_box_6_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Box 6: Output tax due"
    )
    
    # Currency
    currency = models.CharField(
        max_length=3,
        default='SGD',
        help_text="Order currency"
    )
    
    # Payment details
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        help_text="Payment method used"
    )
    
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Payment gateway reference"
    )
    
    # Shipping details
    shipping_method = models.CharField(
        max_length=50,
        blank=True,
        help_text="Shipping method/carrier"
    )
    
    shipping_address = models.JSONField(
        null=True,
        blank=True,
        help_text="Shipping address snapshot"
    )
    
    billing_address = models.JSONField(
        null=True,
        blank=True,
        help_text="Billing address snapshot"
    )
    
    # Tracking
    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Shipment tracking number"
    )
    
    carrier = models.CharField(
        max_length=50,
        blank=True,
        help_text="Shipping carrier name"
    )
    
    # Dates
    order_date = models.DateTimeField(
        default=timezone.now,
        help_text="When order was placed"
    )
    
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When payment was received"
    )
    
    shipped_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When order was shipped"
    )
    
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When order was delivered"
    )
    
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When order was cancelled"
    )
    
    # Notes
    customer_notes = models.TextField(
        blank=True,
        help_text="Notes from customer"
    )
    
    internal_notes = models.TextField(
        blank=True,
        help_text="Internal staff notes"
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional order metadata"
    )
    
    # Audit
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_orders',
        help_text="User who created this order"
    )
    
    class Meta:
        db_table = '"commerce"."orders"'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-order_date']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['customer']),
            models.Index(fields=['order_number']),
            models.Index(fields=['order_date']),
        ]
    
    def __str__(self):
        return self.order_number
    
    def can_transition_to(self, new_status: str) -> bool:
        """
        Check if transition to new status is valid.
        
        Args:
            new_status: Target status
            
        Returns:
            True if transition is allowed
        """
        return new_status in VALID_STATUS_TRANSITIONS.get(self.status, [])
    
    def confirm(self):
        """
        Confirm order (pending → confirmed).
        
        Raises:
            ValueError: If transition is not valid
        """
        if not self.can_transition_to('confirmed'):
            raise ValueError(f"Cannot confirm order in {self.status} status")
        self.status = 'confirmed'
        self.save(update_fields=['status', 'updated_at'])
    
    def process(self):
        """
        Start processing order (confirmed → processing).
        
        Raises:
            ValueError: If transition is not valid
        """
        if not self.can_transition_to('processing'):
            raise ValueError(f"Cannot process order in {self.status} status")
        self.status = 'processing'
        self.save(update_fields=['status', 'updated_at'])
    
    def ship(self, tracking_number: str = '', carrier: str = ''):
        """
        Mark order as shipped (processing → shipped).
        
        Args:
            tracking_number: Shipment tracking number
            carrier: Shipping carrier name
            
        Raises:
            ValueError: If transition is not valid
        """
        if not self.can_transition_to('shipped'):
            raise ValueError(f"Cannot ship order in {self.status} status")
        self.status = 'shipped'
        self.fulfillment_status = 'fulfilled'
        self.shipped_at = timezone.now()
        self.tracking_number = tracking_number
        self.carrier = carrier
        self.save(update_fields=[
            'status', 'fulfillment_status', 'shipped_at',
            'tracking_number', 'carrier', 'updated_at'
        ])
    
    def deliver(self):
        """
        Mark order as delivered (shipped → delivered).
        
        Raises:
            ValueError: If transition is not valid
        """
        if not self.can_transition_to('delivered'):
            raise ValueError(f"Cannot deliver order in {self.status} status")
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save(update_fields=['status', 'delivered_at', 'updated_at'])
    
    def cancel(self, reason: str = ''):
        """
        Cancel order (various → cancelled).
        
        Args:
            reason: Cancellation reason (stored in internal_notes)
            
        Raises:
            ValueError: If transition is not valid
        """
        if not self.can_transition_to('cancelled'):
            raise ValueError(f"Cannot cancel order in {self.status} status")
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        if reason:
            self.internal_notes = f"{self.internal_notes}\nCancelled: {reason}".strip()
        self.save(update_fields=['status', 'cancelled_at', 'internal_notes', 'updated_at'])
    
    def mark_paid(self, payment_reference: str = ''):
        """
        Mark order as paid.
        
        Args:
            payment_reference: Payment gateway reference
        """
        self.payment_status = 'paid'
        self.paid_at = timezone.now()
        if payment_reference:
            self.payment_reference = payment_reference
        self.save(update_fields=['payment_status', 'paid_at', 'payment_reference', 'updated_at'])
    
    def calculate_gst_reporting(self):
        """
        Calculate GST amounts for F5 reporting.
        
        Sets gst_box_1_amount (standard-rated supplies) and
        gst_box_6_amount (output tax due).
        """
        box_1 = Decimal('0.00')  # Standard-rated supplies
        box_6 = Decimal('0.00')  # Output tax
        
        for item in self.items.all():
            if item.gst_code == 'SR':
                box_1 += item.line_total
                box_6 += item.gst_amount
        
        self.gst_box_1_amount = box_1
        self.gst_box_6_amount = box_6
        self.save(update_fields=['gst_box_1_amount', 'gst_box_6_amount', 'updated_at'])
    
    @property
    def is_paid(self) -> bool:
        """Check if order is fully paid."""
        return self.payment_status == 'paid'
    
    @property
    def is_fulfilled(self) -> bool:
        """Check if order is fully fulfilled."""
        return self.fulfillment_status == 'fulfilled'
    
    @property
    def can_be_cancelled(self) -> bool:
        """Check if order can still be cancelled."""
        return self.can_transition_to('cancelled')


class OrderItem(models.Model):
    """
    Individual line item in an order.
    
    Stores product snapshot (sku, name, price) at time of order
    so order history remains accurate even if products change.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=None,
        editable=False
    )
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Order this item belongs to"
    )
    
    # For partitioned table FK (not used in Django, but here for reference)
    order_date = models.DateTimeField(
        help_text="Order date (for partition alignment)"
    )
    
    product = models.ForeignKey(
        'commerce.Product',
        on_delete=models.PROTECT,
        related_name='order_items',
        help_text="Product ordered"
    )
    
    variant = models.ForeignKey(
        'commerce.ProductVariant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
        help_text="Product variant if applicable"
    )
    
    # Product snapshot (preserved even if product changes)
    sku = models.CharField(
        max_length=50,
        help_text="Product SKU at time of order"
    )
    
    name = models.CharField(
        max_length=200,
        help_text="Product name at time of order"
    )
    
    # Quantity
    quantity = models.PositiveIntegerField(
        help_text="Quantity ordered"
    )
    
    # Pricing
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Unit price at time of order"
    )
    
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Discount on this line item"
    )
    
    # GST
    gst_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        help_text="GST rate applied"
    )
    
    gst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="GST amount for this line"
    )
    
    gst_code = models.CharField(
        max_length=2,
        help_text="GST code applied"
    )
    
    # Line total (includes GST)
    line_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total for this line item including GST"
    )
    
    # Fulfillment tracking
    fulfilled_quantity = models.PositiveIntegerField(
        default=0,
        help_text="Quantity fulfilled/shipped"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = '"commerce"."order_items"'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name='order_item_quantity_positive',
            ),
        ]
    
    def __str__(self):
        return f"{self.quantity}x {self.name}"
    
    def save(self, *args, **kwargs):
        """Generate UUID if not set and sync order_date."""
        if self.id is None:
            import uuid
            self.id = uuid.uuid4()
        # Sync order_date from parent order
        if self.order:
            self.order_date = self.order.order_date
        super().save(*args, **kwargs)
    
    @property
    def is_fulfilled(self) -> bool:
        """Check if this item is fully fulfilled."""
        return self.fulfilled_quantity >= self.quantity
    
    @property
    def pending_quantity(self) -> int:
        """Get quantity still pending fulfillment."""
        return max(0, self.quantity - self.fulfilled_quantity)
    
    def calculate_totals(self):
        """
        Calculate line totals from quantity and unit_price.
        
        Should be called before saving when creating from cart.
        """
        subtotal = self.quantity * self.unit_price - self.discount_amount
        
        if self.gst_code == 'SR':
            self.gst_amount = round(subtotal * self.gst_rate, 2)
        else:
            self.gst_amount = Decimal('0.00')
        
        self.line_total = subtotal + self.gst_amount
