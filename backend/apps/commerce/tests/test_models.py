"""
Unit tests for commerce models.

Tests:
- Category hierarchy
- Product GST calculation
- Customer B2B and consent fields
- Cart expiry and totals
- Order status transitions
"""
import pytest
from decimal import Decimal
from datetime import timedelta

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.commerce.models import (
    Category, Product, ProductVariant,
    Customer, CustomerAddress,
    Cart, CartItem, Order, OrderItem,
    VALID_STATUS_TRANSITIONS,
)
from apps.commerce.tests.factories import (
    CategoryFactory, ProductFactory, ProductVariantFactory,
    CustomerFactory, CustomerAddressFactory,
    CartFactory, GuestCartFactory, CartItemFactory,
    OrderFactory, OrderItemFactory,
)


pytestmark = pytest.mark.django_db


# =============================================================================
# CATEGORY TESTS
# =============================================================================

class TestCategoryModel:
    """Tests for Category model."""
    
    def test_create_category(self):
        """Test basic category creation."""
        category = CategoryFactory()
        assert category.id is not None
        assert category.name
        assert category.slug
        assert category.is_active is True
    
    def test_category_hierarchy(self):
        """Test parent-child category relationship."""
        parent = CategoryFactory(name="Parent")
        child = CategoryFactory(company=parent.company, parent=parent, name="Child")
        
        assert child.parent == parent
        assert child in parent.children.all()
    
    def test_get_ancestors(self):
        """Test ancestor traversal."""
        root = CategoryFactory(name="Root")
        level1 = CategoryFactory(company=root.company, parent=root, name="Level 1")
        level2 = CategoryFactory(company=root.company, parent=level1, name="Level 2")
        
        ancestors = level2.get_ancestors()
        assert len(ancestors) == 2
        assert ancestors[0] == level1
        assert ancestors[1] == root
    
    def test_depth_property(self):
        """Test depth calculation."""
        root = CategoryFactory()
        child = CategoryFactory(company=root.company, parent=root)
        grandchild = CategoryFactory(company=root.company, parent=child)
        
        assert root.depth == 0
        assert child.depth == 1
        assert grandchild.depth == 2
    
    def test_slug_uniqueness_per_company(self):
        """Test that slug must be unique within company."""
        cat1 = CategoryFactory(slug="test-slug")
        with pytest.raises(IntegrityError):
            CategoryFactory(company=cat1.company, slug="test-slug")


# =============================================================================
# PRODUCT TESTS
# =============================================================================

class TestProductModel:
    """Tests for Product model."""
    
    def test_create_product(self):
        """Test basic product creation."""
        product = ProductFactory()
        assert product.id is not None
        assert product.sku
        assert isinstance(product.base_price, Decimal)
    
    def test_gst_code_default(self):
        """Test GST code defaults to Standard Rated."""
        product = ProductFactory()
        assert product.gst_code == 'SR'
        assert product.gst_rate == Decimal('0.09')
    
    def test_calculate_gst_standard_rated(self):
        """Test GST calculation for SR products."""
        product = ProductFactory(
            base_price=Decimal('100.00'),
            gst_code='SR',
            gst_rate=Decimal('0.09')
        )
        subtotal, gst, total = product.calculate_gst(quantity=2)
        
        assert subtotal == Decimal('200.00')
        assert gst == Decimal('18.00')
        assert total == Decimal('218.00')
    
    def test_calculate_gst_zero_rated(self):
        """Test GST calculation for ZR products."""
        product = ProductFactory(
            base_price=Decimal('100.00'),
            gst_code='ZR'
        )
        subtotal, gst, total = product.calculate_gst(quantity=2)
        
        assert subtotal == Decimal('200.00')
        assert gst == Decimal('0.00')
        assert total == Decimal('200.00')
    
    def test_is_on_sale(self):
        """Test sale detection."""
        product = ProductFactory(
            base_price=Decimal('80.00'),
            compare_at_price=Decimal('100.00')
        )
        assert product.is_on_sale is True
        
        product.compare_at_price = None
        assert product.is_on_sale is False
    
    def test_sku_uniqueness_per_company(self):
        """Test SKU uniqueness within company."""
        prod1 = ProductFactory(sku="UNIQUE-SKU")
        with pytest.raises(IntegrityError):
            ProductFactory(company=prod1.company, sku="UNIQUE-SKU")


class TestProductVariantModel:
    """Tests for ProductVariant model."""
    
    def test_effective_price(self):
        """Test variant effective price calculation."""
        product = ProductFactory(base_price=Decimal('100.00'))
        variant = ProductVariantFactory(
            product=product,
            price_adjustment=Decimal('10.00')
        )
        assert variant.effective_price == Decimal('110.00')
    
    def test_negative_price_adjustment(self):
        """Test negative price adjustment."""
        product = ProductFactory(base_price=Decimal('100.00'))
        variant = ProductVariantFactory(
            product=product,
            price_adjustment=Decimal('-5.00')
        )
        assert variant.effective_price == Decimal('95.00')


# =============================================================================
# CUSTOMER TESTS
# =============================================================================

class TestCustomerModel:
    """Tests for Customer model."""
    
    def test_create_customer(self):
        """Test basic customer creation."""
        customer = CustomerFactory()
        assert customer.id is not None
        assert customer.email
        assert customer.customer_type == 'retail'
    
    def test_full_name_property(self):
        """Test full name generation."""
        customer = CustomerFactory(first_name="John", last_name="Doe")
        assert customer.full_name == "John Doe"
    
    def test_b2b_customer(self):
        """Test B2B customer with credit."""
        customer = CustomerFactory(
            customer_type='wholesale',
            company_uen='123456789A',
            credit_limit=Decimal('10000.00'),
            credit_used=Decimal('3000.00')
        )
        assert customer.is_b2b is True
        assert customer.available_credit == Decimal('7000.00')
    
    def test_has_available_credit(self):
        """Test credit availability check."""
        customer = CustomerFactory(
            credit_limit=Decimal('1000.00'),
            credit_used=Decimal('800.00')
        )
        assert customer.has_available_credit(Decimal('200.00')) is True
        assert customer.has_available_credit(Decimal('201.00')) is False
    
    def test_email_uniqueness_per_company(self):
        """Test email uniqueness within company."""
        cust1 = CustomerFactory(email="test@example.com")
        with pytest.raises(IntegrityError):
            CustomerFactory(company=cust1.company, email="test@example.com")


# =============================================================================
# CART TESTS
# =============================================================================

class TestCartModel:
    """Tests for Cart model."""
    
    def test_create_customer_cart(self):
        """Test cart with customer."""
        cart = CartFactory()
        assert cart.customer is not None
        assert cart.session_id is None
        assert cart.is_guest is False
    
    def test_create_guest_cart(self):
        """Test guest cart with session_id."""
        cart = GuestCartFactory()
        assert cart.customer is None
        assert cart.session_id is not None
        assert cart.is_guest is True
    
    def test_cart_expiry(self):
        """Test cart expiry detection."""
        cart = CartFactory()
        assert cart.is_expired is False
        
        cart.expires_at = timezone.now() - timedelta(hours=1)
        assert cart.is_expired is True
    
    def test_calculate_totals(self):
        """Test cart totals calculation."""
        cart = CartFactory()
        product = ProductFactory(
            company=cart.company,
            base_price=Decimal('50.00'),
            gst_code='SR',
            gst_rate=Decimal('0.09')
        )
        CartItemFactory(cart=cart, product=product, quantity=2, unit_price=product.base_price)
        
        totals = cart.calculate_totals()
        assert totals['subtotal'] == Decimal('100.00')
        assert totals['gst_amount'] == Decimal('9.00')
        assert totals['total'] == Decimal('109.00')


# =============================================================================
# ORDER TESTS
# =============================================================================

class TestOrderModel:
    """Tests for Order model."""
    
    def test_create_order(self):
        """Test basic order creation."""
        order = OrderFactory()
        assert order.order_number
        assert order.status == 'pending'
        assert isinstance(order.total_amount, Decimal)
    
    def test_valid_status_transitions(self):
        """Test order status state machine."""
        order = OrderFactory(status='pending')
        
        # Valid transitions from pending
        assert order.can_transition_to('confirmed') is True
        assert order.can_transition_to('cancelled') is True
        assert order.can_transition_to('shipped') is False
    
    def test_confirm_order(self):
        """Test order confirmation."""
        order = OrderFactory(status='pending')
        order.confirm()
        assert order.status == 'confirmed'
    
    def test_invalid_transition_raises(self):
        """Test invalid transition raises ValueError."""
        order = OrderFactory(status='pending')
        with pytest.raises(ValueError):
            order.ship()  # Can't ship without confirming first
    
    def test_ship_order(self):
        """Test shipping with tracking."""
        order = OrderFactory(status='processing')
        order.ship(tracking_number='TRK123', carrier='DHL')
        
        assert order.status == 'shipped'
        assert order.tracking_number == 'TRK123'
        assert order.carrier == 'DHL'
        assert order.shipped_at is not None
    
    def test_cancel_order(self):
        """Test order cancellation."""
        order = OrderFactory(status='pending')
        order.cancel(reason="Customer request")
        
        assert order.status == 'cancelled'
        assert order.cancelled_at is not None
        assert "Customer request" in order.internal_notes


class TestOrderItemModel:
    """Tests for OrderItem model."""
    
    def test_line_total_calculation(self):
        """Test line total with GST."""
        item = OrderItemFactory(
            unit_price=Decimal('50.00'),
            quantity=2,
            gst_rate=Decimal('0.09'),
            gst_code='SR'
        )
        item.calculate_totals()
        
        assert item.gst_amount == Decimal('9.00')
        assert item.line_total == Decimal('109.00')
    
    def test_fulfillment_tracking(self):
        """Test fulfillment quantity tracking."""
        item = OrderItemFactory(quantity=5, fulfilled_quantity=3)
        
        assert item.is_fulfilled is False
        assert item.pending_quantity == 2
        
        item.fulfilled_quantity = 5
        assert item.is_fulfilled is True
        assert item.pending_quantity == 0
