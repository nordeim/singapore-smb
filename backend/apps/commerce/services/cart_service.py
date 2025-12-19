"""
Cart service for business logic.

Handles:
- Cart creation for guest/customer
- Add/remove items with price snapshot
- Cart totals calculation
- Guest cart merge on login
- Checkout to order
"""
from decimal import Decimal
from typing import Optional
import uuid

from django.db import transaction
from django.utils import timezone

from apps.commerce.models import (
    Cart, CartItem, Product, ProductVariant, Customer, Order, OrderItem
)


class CartService:
    """Service class for cart business logic."""
    
    @staticmethod
    def get_or_create_cart(
        company,
        customer: Optional[Customer] = None,
        session_id: Optional[str] = None
    ) -> Cart:
        """
        Get or create a cart for customer or guest.
        
        Args:
            company: Company instance
            customer: Optional customer (for logged-in users)
            session_id: Session ID (for guests)
            
        Returns:
            Active Cart instance
        """
        if customer:
            cart = Cart.objects.filter(
                company=company,
                customer=customer,
                status='active'
            ).first()
            
            if not cart:
                cart = Cart.objects.create(
                    company=company,
                    customer=customer
                )
            elif cart.is_expired:
                cart.extend_expiry()
        
        elif session_id:
            cart = Cart.objects.filter(
                company=company,
                session_id=session_id,
                status='active'
            ).first()
            
            if not cart:
                cart = Cart.objects.create(
                    company=company,
                    session_id=session_id
                )
            elif cart.is_expired:
                cart.extend_expiry()
        else:
            raise ValueError("Either customer or session_id required")
        
        return cart
    
    @staticmethod
    @transaction.atomic
    def add_item(
        cart: Cart,
        product: Product,
        variant: Optional[ProductVariant] = None,
        quantity: int = 1
    ) -> CartItem:
        """
        Add item to cart with price snapshot.
        
        If item already exists, updates quantity.
        
        Args:
            cart: Cart instance
            product: Product to add
            variant: Optional variant
            quantity: Quantity to add
            
        Returns:
            CartItem instance
        """
        # Get effective price
        if variant:
            unit_price = variant.effective_price
        else:
            unit_price = product.base_price
        
        # Check if item already in cart
        cart_item = CartItem.objects.filter(
            cart=cart,
            product=product,
            variant=variant
        ).first()
        
        if cart_item:
            # Update quantity
            cart_item.quantity += quantity
            cart_item.save(update_fields=['quantity', 'updated_at'])
        else:
            # Create new item
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                variant=variant,
                quantity=quantity,
                unit_price=unit_price
            )
        
        # Extend cart expiry on activity
        cart.extend_expiry()
        
        return cart_item
    
    @staticmethod
    def update_item_quantity(cart_item: CartItem, quantity: int) -> CartItem:
        """
        Update cart item quantity.
        
        Args:
            cart_item: CartItem instance
            quantity: New quantity (must be > 0)
            
        Returns:
            Updated CartItem instance
            
        Raises:
            ValueError: If quantity <= 0
        """
        cart_item.update_quantity(quantity)
        cart_item.cart.extend_expiry()
        return cart_item
    
    @staticmethod
    def remove_item(cart_item: CartItem) -> None:
        """
        Remove item from cart.
        
        Args:
            cart_item: CartItem to remove
        """
        cart = cart_item.cart
        cart_item.delete()
        cart.extend_expiry()
    
    @staticmethod
    def calculate_totals(cart: Cart) -> dict:
        """
        Calculate cart totals with GST.
        
        Args:
            cart: Cart instance
            
        Returns:
            Dict with subtotal, gst_amount, total, item_count
        """
        return cart.calculate_totals()
    
    @staticmethod
    @transaction.atomic
    def merge_guest_cart(guest_session_id: str, customer: Customer) -> Cart | None:
        """
        Merge guest cart into customer cart on login.
        
        Args:
            guest_session_id: Session ID of guest cart
            customer: Customer to merge into
            
        Returns:
            Customer cart with merged items, or None if no guest cart
        """
        guest_cart = Cart.objects.filter(
            session_id=guest_session_id,
            status='active'
        ).first()
        
        if not guest_cart:
            return None
        
        # Get or create customer cart
        customer_cart = CartService.get_or_create_cart(
            company=guest_cart.company,
            customer=customer
        )
        
        # Merge items
        for guest_item in guest_cart.items.all():
            existing_item = customer_cart.items.filter(
                product=guest_item.product,
                variant=guest_item.variant
            ).first()
            
            if existing_item:
                existing_item.quantity += guest_item.quantity
                existing_item.save(update_fields=['quantity', 'updated_at'])
            else:
                guest_item.cart = customer_cart
                guest_item.save(update_fields=['cart', 'updated_at'])
        
        # Mark guest cart as merged
        guest_cart.status = 'merged'
        guest_cart.save(update_fields=['status', 'updated_at'])
        
        return customer_cart
    
    @staticmethod
    @transaction.atomic
    def checkout(
        cart: Cart,
        shipping_address: dict,
        billing_address: dict | None = None,
        payment_method: str = '',
        shipping_method: str = '',
        customer_notes: str = ''
    ) -> Order:
        """
        Convert cart to order.
        
        Args:
            cart: Cart to checkout
            shipping_address: Shipping address dict
            billing_address: Billing address dict (optional, defaults to shipping)
            payment_method: Payment method string
            shipping_method: Shipping method string
            customer_notes: Notes from customer
            
        Returns:
            Created Order instance
            
        Raises:
            ValueError: If cart is empty or expired
        """
        if cart.is_expired:
            raise ValueError("Cart has expired")
        
        active_items = cart.items.filter(is_saved_for_later=False)
        if not active_items.exists():
            raise ValueError("Cart is empty")
        
        # Calculate totals
        totals = cart.calculate_totals()
        
        # Generate order number (using timestamp + random for now)
        # TODO: Use core.sequences for proper order numbering
        order_number = f"ORD-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Create order
        order = Order.objects.create(
            company=cart.company,
            customer=cart.customer,
            order_number=order_number,
            subtotal=totals['subtotal'],
            gst_amount=totals['gst_amount'],
            total_amount=totals['total'],
            shipping_address=shipping_address,
            billing_address=billing_address or shipping_address,
            payment_method=payment_method,
            shipping_method=shipping_method,
            customer_notes=customer_notes,
        )
        
        # Create order items from cart items
        for cart_item in active_items:
            product = cart_item.product
            
            # Calculate line GST
            line_subtotal = cart_item.line_total
            if product.gst_code == 'SR':
                line_gst = round(line_subtotal * product.gst_rate, 2)
            else:
                line_gst = Decimal('0.00')
            
            OrderItem.objects.create(
                order=order,
                order_date=order.order_date,
                product=product,
                variant=cart_item.variant,
                sku=cart_item.variant.sku if cart_item.variant else product.sku,
                name=product.name,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                gst_rate=product.gst_rate,
                gst_amount=line_gst,
                gst_code=product.gst_code,
                line_total=line_subtotal + line_gst,
            )
        
        # Mark cart as converted
        cart.mark_converted(order.id)
        
        # Calculate GST reporting amounts
        order.calculate_gst_reporting()
        
        return order
    
    @staticmethod
    @transaction.atomic
    def cleanup_expired_carts(company=None) -> int:
        """
        Mark expired carts as abandoned.
        
        Args:
            company: Optional company to filter by
            
        Returns:
            Number of carts marked abandoned
        """
        qs = Cart.objects.filter(
            status='active',
            expires_at__lt=timezone.now()
        )
        
        if company:
            qs = qs.filter(company=company)
        
        count = qs.update(status='abandoned')
        return count
