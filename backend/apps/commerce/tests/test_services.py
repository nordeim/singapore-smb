"""
Unit tests for commerce services.

Tests:
- ProductService (create, search, GST calculation)
- CartService (add, merge, checkout)
- OrderService (transitions, GST reporting)
"""
import pytest
from decimal import Decimal
from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone

from apps.commerce.models import Cart, Order
from apps.commerce.services import ProductService, CartService, OrderService
from apps.commerce.tests.factories import (
    CategoryFactory, ProductFactory, ProductVariantFactory,
    CustomerFactory, CustomerAddressFactory,
    CartFactory, GuestCartFactory, CartItemFactory,
    OrderFactory, OrderItemFactory,
)
from apps.accounts.tests.factories import CompanyFactory


pytestmark = pytest.mark.django_db


# =============================================================================
# PRODUCT SERVICE TESTS
# =============================================================================

class TestProductService:
    """Tests for ProductService."""
    
    def test_create_product(self):
        """Test product creation via service."""
        company = CompanyFactory()
        category = CategoryFactory(company=company)
        
        product = ProductService.create_product(
            company=company,
            data={
                'sku': 'TEST-001',
                'name': 'Test Product',
                'slug': 'test-product',
                'base_price': Decimal('99.99'),
                'gst_code': 'SR',
                'gst_rate': Decimal('0.09'),
                'status': 'active',
                'category_id': str(category.id),
            }
        )
        
        assert product.id is not None
        assert product.sku == 'TEST-001'
        assert product.category == category
    
    def test_create_product_with_variants(self):
        """Test product creation with variants."""
        company = CompanyFactory()
        
        product = ProductService.create_product(
            company=company,
            data={
                'sku': 'TEST-002',
                'name': 'Product with Variants',
                'slug': 'product-variants',
                'base_price': Decimal('50.00'),
                'gst_code': 'SR',
                'gst_rate': Decimal('0.09'),
                'status': 'active',
            },
            variants=[
                {'sku': 'TEST-002-S', 'name': 'Small', 'options': {'size': 'S'}},
                {'sku': 'TEST-002-M', 'name': 'Medium', 'options': {'size': 'M'}},
            ]
        )
        
        assert product.variants.count() == 2
    
    def test_calculate_price_with_gst(self):
        """Test price calculation with GST."""
        product = ProductFactory(
            base_price=Decimal('100.00'),
            gst_code='SR',
            gst_rate=Decimal('0.09')
        )
        
        subtotal, gst, total = ProductService.calculate_price_with_gst(
            product, quantity=3
        )
        
        assert subtotal == Decimal('300.00')
        assert gst == Decimal('27.00')
        assert total == Decimal('327.00')
    
    def test_calculate_price_with_variant(self):
        """Test price calculation with variant adjustment."""
        product = ProductFactory(base_price=Decimal('100.00'))
        variant = ProductVariantFactory(product=product, price_adjustment=Decimal('20.00'))
        
        subtotal, gst, total = ProductService.calculate_price_with_gst(
            product, quantity=2, variant=variant
        )
        
        assert subtotal == Decimal('240.00')  # (100 + 20) * 2
    
    def test_search_products(self):
        """Test product search."""
        company = CompanyFactory()
        ProductFactory(company=company, name='Blue Widget', status='active')
        ProductFactory(company=company, name='Red Gadget', status='active')
        ProductFactory(company=company, name='Blue Gadget', status='archived')
        
        # Search should find active products matching 'blue'
        results = ProductService.search(company, 'blue')
        assert len(results) == 1
        assert results[0].name == 'Blue Widget'


# =============================================================================
# CART SERVICE TESTS
# =============================================================================

class TestCartService:
    """Tests for CartService."""
    
    def test_get_or_create_cart_for_customer(self):
        """Test cart creation for logged-in customer."""
        customer = CustomerFactory()
        
        cart = CartService.get_or_create_cart(
            company=customer.company,
            customer=customer
        )
        
        assert cart.customer == customer
        assert cart.status == 'active'
    
    def test_get_or_create_cart_for_guest(self):
        """Test cart creation for guest."""
        company = CompanyFactory()
        session_id = 'test_session_123'
        
        cart = CartService.get_or_create_cart(
            company=company,
            session_id=session_id
        )
        
        assert cart.customer is None
        assert cart.session_id == session_id
    
    def test_add_item_to_cart(self):
        """Test adding item to cart."""
        cart = CartFactory()
        product = ProductFactory(company=cart.company, base_price=Decimal('25.00'))
        
        cart_item = CartService.add_item(cart, product, quantity=2)
        
        assert cart_item.quantity == 2
        assert cart_item.unit_price == Decimal('25.00')
    
    def test_add_existing_item_increases_quantity(self):
        """Test adding same product increases quantity."""
        cart = CartFactory()
        product = ProductFactory(company=cart.company)
        
        CartService.add_item(cart, product, quantity=2)
        CartService.add_item(cart, product, quantity=3)
        
        assert cart.items.count() == 1
        assert cart.items.first().quantity == 5
    
    def test_merge_guest_cart(self):
        """Test merging guest cart on login."""
        company = CompanyFactory()
        customer = CustomerFactory(company=company)
        
        # Create guest cart with items
        guest_cart = GuestCartFactory(company=company)
        product = ProductFactory(company=company)
        CartItemFactory(cart=guest_cart, product=product, quantity=2)
        
        # Merge on login
        merged_cart = CartService.merge_guest_cart(
            guest_session_id=guest_cart.session_id,
            customer=customer
        )
        
        assert merged_cart.customer == customer
        assert merged_cart.items.count() == 1
        
        # Guest cart should be marked as merged
        guest_cart.refresh_from_db()
        assert guest_cart.status == 'merged'
    
    def test_checkout_creates_order(self):
        """Test checkout creates order from cart."""
        cart = CartFactory()
        product = ProductFactory(
            company=cart.company,
            base_price=Decimal('50.00'),
            gst_code='SR',
            gst_rate=Decimal('0.09')
        )
        CartItemFactory(cart=cart, product=product, quantity=2, unit_price=product.base_price)
        
        shipping_address = {
            'recipient_name': 'Test Customer',
            'address_line1': '123 Test St',
            'postal_code': '123456',
            'country': 'SG',
        }
        
        order = CartService.checkout(cart, shipping_address)
        
        assert order.order_number
        assert order.subtotal == Decimal('100.00')
        assert order.items.count() == 1
        
        # Cart should be marked as converted
        cart.refresh_from_db()
        assert cart.status == 'converted'
    
    def test_checkout_empty_cart_raises(self):
        """Test checkout with empty cart raises error."""
        cart = CartFactory()
        
        with pytest.raises(ValueError, match="Cart is empty"):
            CartService.checkout(cart, {'address': 'test'})
    
    def test_cleanup_expired_carts(self):
        """Test expired cart cleanup."""
        company = CompanyFactory()
        
        # Create expired cart
        expired_cart = CartFactory(company=company)
        expired_cart.expires_at = timezone.now() - timedelta(hours=1)
        expired_cart.save()
        
        # Create active cart
        active_cart = CartFactory(company=company)
        
        count = CartService.cleanup_expired_carts(company)
        
        assert count == 1
        
        expired_cart.refresh_from_db()
        assert expired_cart.status == 'abandoned'
        
        active_cart.refresh_from_db()
        assert active_cart.status == 'active'


# =============================================================================
# ORDER SERVICE TESTS
# =============================================================================

class TestOrderService:
    """Tests for OrderService."""
    
    def test_confirm_order(self):
        """Test order confirmation."""
        order = OrderFactory(status='pending')
        
        OrderService.confirm(order)
        
        assert order.status == 'confirmed'
    
    def test_process_order(self):
        """Test order processing."""
        order = OrderFactory(status='confirmed')
        
        OrderService.process(order)
        
        assert order.status == 'processing'
    
    def test_ship_order(self):
        """Test order shipping."""
        order = OrderFactory(status='processing')
        
        OrderService.ship(order, tracking_number='TRK-123', carrier='SingPost')
        
        assert order.status == 'shipped'
        assert order.tracking_number == 'TRK-123'
        assert order.carrier == 'SingPost'
        assert order.shipped_at is not None
    
    def test_deliver_order(self):
        """Test order delivery."""
        order = OrderFactory(status='shipped')
        
        OrderService.deliver(order)
        
        assert order.status == 'delivered'
        assert order.delivered_at is not None
    
    def test_cancel_order(self):
        """Test order cancellation."""
        order = OrderFactory(status='pending')
        
        OrderService.cancel(order, reason="Customer changed mind")
        
        assert order.status == 'cancelled'
        assert "Customer changed mind" in order.internal_notes
    
    def test_invalid_transition_raises(self):
        """Test invalid status transition raises error."""
        order = OrderFactory(status='delivered')
        
        with pytest.raises(ValueError):
            OrderService.cancel(order)
    
    def test_calculate_period_gst_totals(self):
        """Test GST totals for reporting period."""
        company = CompanyFactory()
        
        # Create orders with GST amounts
        order1 = OrderFactory(
            company=company,
            status='delivered',
            gst_box_1_amount=Decimal('100.00'),
            gst_box_6_amount=Decimal('9.00')
        )
        order2 = OrderFactory(
            company=company,
            status='shipped',
            gst_box_1_amount=Decimal('200.00'),
            gst_box_6_amount=Decimal('18.00')
        )
        
        start_date = timezone.now() - timedelta(days=30)
        end_date = timezone.now() + timedelta(days=1)
        
        totals = OrderService.calculate_period_gst_totals(
            company, start_date, end_date
        )
        
        assert totals['box_1_standard_rated_supplies'] == Decimal('300.00')
        assert totals['box_6_output_tax'] == Decimal('27.00')
        assert totals['order_count'] == 2
