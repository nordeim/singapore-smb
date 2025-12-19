"""
Factory Boy factories for commerce models.

Provides reliable test data generation with proper DECIMAL handling
and GST code defaults.
"""
import uuid
from decimal import Decimal

import factory
from factory.django import DjangoModelFactory

from apps.commerce.models import (
    Category, Product, ProductVariant,
    Customer, CustomerAddress,
    Cart, CartItem, Order, OrderItem,
)
from apps.accounts.tests.factories import CompanyFactory, UserFactory


class CategoryFactory(DjangoModelFactory):
    """Factory for Category model."""
    
    class Meta:
        model = Category
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    parent = None
    name = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.LazyAttribute(lambda o: o.name.lower().replace(' ', '-'))
    description = factory.Faker('paragraph')
    is_active = True
    sort_order = factory.Sequence(lambda n: n)


class ProductFactory(DjangoModelFactory):
    """Factory for Product model."""
    
    class Meta:
        model = Product
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    category = factory.SubFactory(CategoryFactory, company=factory.SelfAttribute('..company'))
    sku = factory.Sequence(lambda n: f"SKU-{n:06d}")
    barcode = factory.Sequence(lambda n: f"8888{n:08d}")
    name = factory.Faker('sentence', nb_words=3)
    slug = factory.LazyAttribute(lambda o: o.name.lower().replace(' ', '-').replace('.', ''))
    description = factory.Faker('paragraph')
    short_description = factory.Faker('sentence')
    
    # Pricing with DECIMAL precision
    base_price = factory.LazyFunction(lambda: Decimal(f"{factory.Faker._get_faker().random_int(10, 500)}.{factory.Faker._get_faker().random_int(0, 99):02d}"))
    cost_price = factory.LazyAttribute(lambda o: o.base_price * Decimal('0.6'))
    compare_at_price = None
    
    # GST defaults to Standard Rated
    gst_code = 'SR'
    gst_rate = Decimal('0.09')
    
    # Inventory
    track_inventory = True
    allow_backorder = False
    low_stock_threshold = 10
    
    status = 'active'
    images = factory.LazyFunction(list)
    attributes = factory.LazyFunction(dict)


class ProductVariantFactory(DjangoModelFactory):
    """Factory for ProductVariant model."""
    
    class Meta:
        model = ProductVariant
    
    id = factory.LazyFunction(uuid.uuid4)
    product = factory.SubFactory(ProductFactory)
    sku = factory.Sequence(lambda n: f"VAR-{n:06d}")
    name = factory.Faker('word')
    options = factory.LazyFunction(lambda: {'size': 'M', 'color': 'Blue'})
    price_adjustment = Decimal('0.00')
    is_active = True


class CustomerFactory(DjangoModelFactory):
    """Factory for Customer model."""
    
    class Meta:
        model = Customer
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    user = None  # Optional link
    email = factory.Faker('email')
    phone = factory.LazyFunction(lambda: f"+65{factory.Faker._get_faker().random_int(80000000, 99999999)}")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    customer_type = 'retail'
    
    # B2B fields
    company_name = ''
    company_uen = ''
    credit_limit = Decimal('0.00')
    credit_used = Decimal('0.00')
    payment_terms = 0
    
    # PDPA defaults
    consent_marketing = False
    consent_analytics = True
    consent_timestamp = None
    
    preferred_language = 'en'
    preferred_currency = 'SGD'
    tags = factory.LazyFunction(list)


class CustomerAddressFactory(DjangoModelFactory):
    """Factory for CustomerAddress model."""
    
    class Meta:
        model = CustomerAddress
    
    id = factory.LazyFunction(uuid.uuid4)
    customer = factory.SubFactory(CustomerFactory)
    address_type = 'shipping'
    is_default = True
    recipient_name = factory.Faker('name')
    phone = factory.LazyFunction(lambda: f"+65{factory.Faker._get_faker().random_int(80000000, 99999999)}")
    address_line1 = factory.Faker('street_address')
    address_line2 = ''
    postal_code = factory.LazyFunction(lambda: str(factory.Faker._get_faker().random_int(100000, 999999)))
    country = 'SG'
    building_name = ''
    unit_number = factory.LazyFunction(lambda: f"#{factory.Faker._get_faker().random_int(1, 30):02d}-{factory.Faker._get_faker().random_int(1, 200):02d}")


class CartFactory(DjangoModelFactory):
    """Factory for Cart model."""
    
    class Meta:
        model = Cart
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    customer = factory.SubFactory(CustomerFactory, company=factory.SelfAttribute('..company'))
    session_id = None  # Use customer by default
    status = 'active'


class GuestCartFactory(CartFactory):
    """Factory for guest (session-based) cart."""
    
    customer = None
    session_id = factory.LazyFunction(lambda: f"session_{uuid.uuid4().hex[:16]}")


class CartItemFactory(DjangoModelFactory):
    """Factory for CartItem model."""
    
    class Meta:
        model = CartItem
    
    id = factory.LazyFunction(uuid.uuid4)
    cart = factory.SubFactory(CartFactory)
    product = factory.SubFactory(ProductFactory, company=factory.SelfAttribute('..cart.company'))
    variant = None
    quantity = factory.LazyFunction(lambda: factory.Faker._get_faker().random_int(1, 5))
    unit_price = factory.LazyAttribute(lambda o: o.product.base_price)
    is_saved_for_later = False


class OrderFactory(DjangoModelFactory):
    """Factory for Order model."""
    
    class Meta:
        model = Order
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    customer = factory.SubFactory(CustomerFactory, company=factory.SelfAttribute('..company'))
    order_number = factory.Sequence(lambda n: f"ORD-{n:08d}")
    
    status = 'pending'
    payment_status = 'pending'
    fulfillment_status = 'unfulfilled'
    
    subtotal = Decimal('100.00')
    discount_amount = Decimal('0.00')
    shipping_amount = Decimal('5.00')
    gst_amount = Decimal('9.45')
    total_amount = Decimal('114.45')
    
    currency = 'SGD'
    
    shipping_address = factory.LazyFunction(lambda: {
        'recipient_name': 'Test Customer',
        'address_line1': '123 Test Street',
        'postal_code': '123456',
        'country': 'SG',
    })
    billing_address = factory.LazyAttribute(lambda o: o.shipping_address)


class OrderItemFactory(DjangoModelFactory):
    """Factory for OrderItem model."""
    
    class Meta:
        model = OrderItem
    
    id = factory.LazyFunction(uuid.uuid4)
    order = factory.SubFactory(OrderFactory)
    order_date = factory.LazyAttribute(lambda o: o.order.order_date)
    product = factory.SubFactory(ProductFactory, company=factory.SelfAttribute('..order.company'))
    variant = None
    sku = factory.LazyAttribute(lambda o: o.product.sku)
    name = factory.LazyAttribute(lambda o: o.product.name)
    quantity = 2
    unit_price = factory.LazyAttribute(lambda o: o.product.base_price)
    discount_amount = Decimal('0.00')
    gst_rate = Decimal('0.09')
    gst_amount = factory.LazyAttribute(lambda o: round(o.unit_price * o.quantity * o.gst_rate, 2))
    gst_code = 'SR'
    line_total = factory.LazyAttribute(lambda o: o.unit_price * o.quantity + o.gst_amount)
    fulfilled_quantity = 0
