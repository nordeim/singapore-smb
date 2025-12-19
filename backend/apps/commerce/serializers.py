"""
DRF serializers for commerce domain.

Implements serializers for all commerce models with:
- Nested representations for related models
- DECIMAL field handling
- GST code validation
- Singapore postal code validation
"""
from decimal import Decimal

from rest_framework import serializers

from apps.commerce.models import (
    Category,
    Product,
    ProductVariant,
    Customer,
    CustomerAddress,
    Cart,
    CartItem,
    Order,
    OrderItem,
    GST_CODE_CHOICES,
    CUSTOMER_TYPE_CHOICES,
)


# =============================================================================
# CATEGORY SERIALIZERS
# =============================================================================

class CategorySerializer(serializers.ModelSerializer):
    """Basic category serializer with parent info."""
    
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    depth = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'image_url',
            'parent', 'parent_name', 'depth',
            'meta_title', 'meta_description',
            'sort_order', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'depth']


class CategoryTreeSerializer(serializers.ModelSerializer):
    """Recursive category serializer for tree structure."""
    
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'image_url',
            'sort_order', 'is_active', 'children',
        ]
    
    def get_children(self, obj):
        """Recursively serialize children."""
        children = obj.children.filter(is_active=True).order_by('sort_order', 'name')
        return CategoryTreeSerializer(children, many=True).data


# =============================================================================
# PRODUCT SERIALIZERS
# =============================================================================

class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for product variants."""
    
    effective_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    options_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'sku', 'barcode', 'name', 'options',
            'price_adjustment', 'effective_price', 'options_display',
            'weight_grams', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'effective_price', 'options_display']


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight product serializer for list views."""
    
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    primary_image = serializers.CharField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'slug', 'short_description',
            'base_price', 'compare_at_price', 'is_on_sale', 'discount_percentage',
            'category', 'category_name', 'status',
            'primary_image', 'gst_code',
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full product serializer with variants and category."""
    
    category = CategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.DecimalField(
        max_digits=5, decimal_places=0, read_only=True
    )
    margin_percentage = serializers.DecimalField(
        max_digits=5, decimal_places=2, read_only=True, allow_null=True
    )
    
    class Meta:
        model = Product
        fields = [
            'id', 'company', 'sku', 'barcode', 'name', 'slug',
            'description', 'short_description',
            'base_price', 'cost_price', 'compare_at_price',
            'is_on_sale', 'discount_percentage', 'margin_percentage',
            'gst_code', 'gst_rate',
            'weight_grams', 'length_cm', 'width_cm', 'height_cm',
            'track_inventory', 'allow_backorder', 'low_stock_threshold',
            'status', 'images', 'attributes',
            'meta_title', 'meta_description',
            'category', 'category_id', 'variants',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'company', 'created_at', 'updated_at',
            'is_on_sale', 'discount_percentage', 'margin_percentage',
        ]
    
    def validate_gst_code(self, value):
        """Validate GST code is one of allowed values."""
        valid_codes = [code[0] for code in GST_CODE_CHOICES]
        if value not in valid_codes:
            raise serializers.ValidationError(
                f"Invalid GST code. Must be one of: {', '.join(valid_codes)}"
            )
        return value


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating products."""
    
    class Meta:
        model = Product
        fields = [
            'sku', 'barcode', 'name', 'slug',
            'description', 'short_description',
            'base_price', 'cost_price', 'compare_at_price',
            'gst_code', 'gst_rate',
            'weight_grams', 'length_cm', 'width_cm', 'height_cm',
            'track_inventory', 'allow_backorder', 'low_stock_threshold',
            'status', 'images', 'attributes',
            'meta_title', 'meta_description',
            'category',
        ]
    
    def validate_gst_code(self, value):
        valid_codes = [code[0] for code in GST_CODE_CHOICES]
        if value not in valid_codes:
            raise serializers.ValidationError(
                f"Invalid GST code. Must be one of: {', '.join(valid_codes)}"
            )
        return value


# =============================================================================
# CUSTOMER SERIALIZERS
# =============================================================================

class CustomerAddressSerializer(serializers.ModelSerializer):
    """Serializer for customer addresses."""
    
    formatted_address = serializers.CharField(source='get_formatted_address', read_only=True)
    
    class Meta:
        model = CustomerAddress
        fields = [
            'id', 'address_type', 'is_default',
            'recipient_name', 'phone',
            'address_line1', 'address_line2',
            'postal_code', 'country',
            'building_name', 'unit_number',
            'formatted_address',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'formatted_address']
    
    def validate_postal_code(self, value):
        """Validate Singapore postal code (6 digits)."""
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError(
                "Singapore postal code must be exactly 6 digits"
            )
        return value


class CustomerSerializer(serializers.ModelSerializer):
    """Full customer serializer with addresses."""
    
    addresses = CustomerAddressSerializer(many=True, read_only=True)
    full_name = serializers.CharField(read_only=True)
    available_credit = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    is_b2b = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Customer
        fields = [
            'id', 'email', 'phone', 'first_name', 'last_name', 'full_name',
            'customer_type', 'is_b2b',
            'company_name', 'company_uen',
            'credit_limit', 'credit_used', 'available_credit', 'payment_terms',
            'consent_marketing', 'consent_analytics',
            'consent_timestamp', 'data_retention_until',
            'preferred_language', 'preferred_currency', 'tags',
            'addresses',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'full_name', 'available_credit', 'is_b2b',
            'consent_timestamp',
        ]
    
    def validate_company_uen(self, value):
        """Validate Singapore UEN format if provided."""
        if value:
            # UEN format: 8-9 alphanumeric characters
            # Common formats: 12345678A, 201234567A, T08SS1234A
            if len(value) < 8 or len(value) > 10:
                raise serializers.ValidationError(
                    "Invalid UEN format"
                )
        return value


# =============================================================================
# CART SERIALIZERS
# =============================================================================

class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True, allow_null=True)
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'variant', 'quantity', 'unit_price',
            'product_name', 'product_sku', 'variant_name',
            'line_total', 'is_saved_for_later',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'line_total',
            'product_name', 'product_sku', 'variant_name',
        ]


class CartSerializer(serializers.ModelSerializer):
    """Full cart serializer with items and totals."""
    
    items = CartItemSerializer(many=True, read_only=True)
    item_count = serializers.IntegerField(read_only=True)
    unique_item_count = serializers.IntegerField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    totals = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'customer', 'session_id', 'status',
            'expires_at', 'is_expired',
            'item_count', 'unique_item_count',
            'items', 'totals',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'is_expired', 'item_count', 'unique_item_count', 'totals',
        ]
    
    def get_totals(self, obj):
        """Calculate cart totals."""
        return obj.calculate_totals()


class AddCartItemSerializer(serializers.Serializer):
    """Serializer for adding item to cart."""
    
    product_id = serializers.UUIDField()
    variant_id = serializers.UUIDField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity."""
    
    quantity = serializers.IntegerField(min_value=1)


# =============================================================================
# ORDER SERIALIZERS
# =============================================================================

class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items."""
    
    is_fulfilled = serializers.BooleanField(read_only=True)
    pending_quantity = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'variant', 'sku', 'name',
            'quantity', 'unit_price', 'discount_amount',
            'gst_rate', 'gst_amount', 'gst_code', 'line_total',
            'fulfilled_quantity', 'is_fulfilled', 'pending_quantity',
        ]
        read_only_fields = [
            'id', 'is_fulfilled', 'pending_quantity',
        ]


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight order serializer for list views."""
    
    customer_name = serializers.CharField(source='customer.full_name', read_only=True, allow_null=True)
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'customer_name',
            'status', 'payment_status', 'fulfillment_status',
            'total_amount', 'currency', 'item_count',
            'order_date',
        ]
    
    def get_item_count(self, obj):
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    """Full order serializer with items."""
    
    customer = CustomerSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    can_be_cancelled = serializers.BooleanField(read_only=True)
    is_paid = serializers.BooleanField(read_only=True)
    is_fulfilled = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer',
            'status', 'payment_status', 'fulfillment_status',
            'subtotal', 'discount_amount', 'shipping_amount',
            'gst_amount', 'total_amount',
            'gst_box_1_amount', 'gst_box_6_amount',
            'currency', 'payment_method', 'payment_reference',
            'shipping_method', 'shipping_address', 'billing_address',
            'tracking_number', 'carrier',
            'order_date', 'paid_at', 'shipped_at', 'delivered_at', 'cancelled_at',
            'customer_notes', 'internal_notes', 'metadata',
            'items',
            'can_be_cancelled', 'is_paid', 'is_fulfilled',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'order_number', 'created_at', 'updated_at',
            'can_be_cancelled', 'is_paid', 'is_fulfilled',
        ]


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating order from cart."""
    
    cart_id = serializers.UUIDField()
    shipping_address_id = serializers.UUIDField(required=False, allow_null=True)
    billing_address_id = serializers.UUIDField(required=False, allow_null=True)
    shipping_address = CustomerAddressSerializer(required=False, allow_null=True)
    billing_address = CustomerAddressSerializer(required=False, allow_null=True)
    payment_method = serializers.CharField(max_length=50, required=False, default='')
    shipping_method = serializers.CharField(max_length=50, required=False, default='')
    customer_notes = serializers.CharField(required=False, default='', allow_blank=True)


class ShipOrderSerializer(serializers.Serializer):
    """Serializer for shipping an order."""
    
    tracking_number = serializers.CharField(max_length=100, required=False, default='')
    carrier = serializers.CharField(max_length=50, required=False, default='')


class CancelOrderSerializer(serializers.Serializer):
    """Serializer for cancelling an order."""
    
    reason = serializers.CharField(required=False, default='', allow_blank=True)
