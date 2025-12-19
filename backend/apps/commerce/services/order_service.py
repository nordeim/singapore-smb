"""
Order service for business logic.

Handles:
- Order creation from cart
- Status transitions with validation
- GST calculation for F5 reporting
- Order number generation
"""
from decimal import Decimal
import uuid

from django.db import transaction
from django.utils import timezone

from apps.commerce.models import Order, OrderItem, Cart


class OrderService:
    """Service class for order business logic."""
    
    @staticmethod
    @transaction.atomic
    def create_from_cart(
        cart: Cart,
        shipping_address: dict,
        billing_address: dict | None = None,
        **kwargs
    ) -> Order:
        """
        Create order from cart.
        
        This is a convenience wrapper around CartService.checkout().
        For full implementation, see CartService.checkout().
        
        Args:
            cart: Cart to convert
            shipping_address: Shipping address dict
            billing_address: Optional billing address
            **kwargs: Additional order fields
            
        Returns:
            Created Order instance
        """
        from apps.commerce.services.cart_service import CartService
        return CartService.checkout(
            cart=cart,
            shipping_address=shipping_address,
            billing_address=billing_address,
            **kwargs
        )
    
    @staticmethod
    def confirm(order: Order) -> Order:
        """
        Confirm an order (pending → confirmed).
        
        Args:
            order: Order to confirm
            
        Returns:
            Confirmed Order instance
            
        Raises:
            ValueError: If transition is invalid
        """
        order.confirm()
        # TODO: Emit event for inventory reservation (Phase 3)
        return order
    
    @staticmethod
    def process(order: Order) -> Order:
        """
        Start processing an order (confirmed → processing).
        
        Args:
            order: Order to process
            
        Returns:
            Processing Order instance
            
        Raises:
            ValueError: If transition is invalid
        """
        order.process()
        return order
    
    @staticmethod
    def ship(
        order: Order,
        tracking_number: str = '',
        carrier: str = ''
    ) -> Order:
        """
        Ship an order (processing → shipped).
        
        Args:
            order: Order to ship
            tracking_number: Shipment tracking number
            carrier: Shipping carrier name
            
        Returns:
            Shipped Order instance
            
        Raises:
            ValueError: If transition is invalid
        """
        order.ship(tracking_number=tracking_number, carrier=carrier)
        # TODO: Emit event for inventory fulfillment (Phase 3)
        return order
    
    @staticmethod
    def deliver(order: Order) -> Order:
        """
        Mark order as delivered (shipped → delivered).
        
        Args:
            order: Order to mark delivered
            
        Returns:
            Delivered Order instance
            
        Raises:
            ValueError: If transition is invalid
        """
        order.deliver()
        return order
    
    @staticmethod
    @transaction.atomic
    def cancel(order: Order, reason: str = '') -> Order:
        """
        Cancel an order.
        
        Args:
            order: Order to cancel
            reason: Cancellation reason
            
        Returns:
            Cancelled Order instance
            
        Raises:
            ValueError: If order cannot be cancelled
        """
        order.cancel(reason=reason)
        # TODO: Emit event for inventory release (Phase 3)
        # TODO: Emit event for refund if paid (Phase 5)
        return order
    
    @staticmethod
    @transaction.atomic
    def refund(
        order: Order,
        items: list[dict] | None = None,
        reason: str = ''
    ) -> Order:
        """
        Refund an order (full or partial).
        
        Args:
            order: Order to refund
            items: Optional list of items to refund with quantities
                   [{'order_item_id': uuid, 'quantity': int}]
            reason: Refund reason
            
        Returns:
            Refunded Order instance
        """
        if items:
            # Partial refund - mark specific items
            refund_amount = Decimal('0.00')
            for item_data in items:
                order_item = order.items.get(id=item_data['order_item_id'])
                refund_qty = item_data.get('quantity', order_item.quantity)
                item_refund = (order_item.line_total / order_item.quantity) * refund_qty
                refund_amount += item_refund
            
            order.payment_status = 'partially_refunded'
            order.internal_notes = f"{order.internal_notes}\nPartial refund: {refund_amount} - {reason}".strip()
        else:
            # Full refund
            order.status = 'refunded'
            order.payment_status = 'refunded'
            order.internal_notes = f"{order.internal_notes}\nFull refund - {reason}".strip()
        
        order.save()
        # TODO: Emit event for payment refund (Phase 5)
        return order
    
    @staticmethod
    def calculate_gst_totals(order: Order) -> Order:
        """
        Calculate GST amounts for F5 reporting.
        
        Sets gst_box_1_amount and gst_box_6_amount.
        
        Args:
            order: Order to calculate GST for
            
        Returns:
            Order with updated GST fields
        """
        order.calculate_gst_reporting()
        return order
    
    @staticmethod
    def generate_order_number(company) -> str:
        """
        Generate unique order number for a company.
        
        Format: ORD-{YYYYMMDD}-{SEQUENCE}
        
        Args:
            company: Company instance
            
        Returns:
            Generated order number string
            
        TODO: Use core.sequences for proper concurrent-safe numbering
        """
        date_part = timezone.now().strftime('%Y%m%d')
        random_part = uuid.uuid4().hex[:8].upper()
        return f"ORD-{date_part}-{random_part}"
    
    @staticmethod
    def get_orders_for_gst_period(
        company,
        start_date,
        end_date
    ):
        """
        Get orders for GST reporting period.
        
        Args:
            company: Company instance
            start_date: Period start date
            end_date: Period end date
            
        Returns:
            QuerySet of orders for the period
        """
        return Order.objects.filter(
            company=company,
            order_date__gte=start_date,
            order_date__lt=end_date,
            status__in=['confirmed', 'processing', 'shipped', 'delivered']
        ).order_by('order_date')
    
    @staticmethod
    def calculate_period_gst_totals(
        company,
        start_date,
        end_date
    ) -> dict:
        """
        Calculate GST totals for a reporting period (IRAS F5).
        
        Args:
            company: Company instance
            start_date: Period start date
            end_date: Period end date
            
        Returns:
            Dict with box_1, box_6 amounts for F5 return
        """
        orders = OrderService.get_orders_for_gst_period(company, start_date, end_date)
        
        box_1 = Decimal('0.00')  # Standard-rated supplies
        box_6 = Decimal('0.00')  # Output tax
        
        for order in orders:
            if order.gst_box_1_amount:
                box_1 += order.gst_box_1_amount
            if order.gst_box_6_amount:
                box_6 += order.gst_box_6_amount
        
        return {
            'box_1_standard_rated_supplies': box_1,
            'box_6_output_tax': box_6,
            'order_count': orders.count(),
        }
