"""
Django admin configuration for commerce models.
"""
from django.contrib import admin

from apps.commerce.models import (
    Category, Product, ProductVariant,
    Customer, CustomerAddress,
    Cart, CartItem, Order, OrderItem,
)


# =============================================================================
# CATEGORY ADMIN
# =============================================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for product categories."""
    
    list_display = ['name', 'parent', 'slug', 'is_active', 'sort_order', 'company']
    list_filter = ['is_active', 'company']
    search_fields = ['name', 'slug']
    ordering = ['company', 'parent', 'sort_order', 'name']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        (None, {
            'fields': ('company', 'parent', 'name', 'slug', 'description')
        }),
        ('Media', {
            'fields': ('image_url',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Display', {
            'fields': ('sort_order', 'is_active')
        }),
    )


# =============================================================================
# PRODUCT ADMIN
# =============================================================================

class ProductVariantInline(admin.TabularInline):
    """Inline for product variants."""
    
    model = ProductVariant
    extra = 0
    fields = ['sku', 'name', 'options', 'price_adjustment', 'is_active']
    readonly_fields = []


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin for products."""
    
    list_display = [
        'sku', 'name', 'base_price', 'gst_code', 'status', 
        'category', 'company'
    ]
    list_filter = ['status', 'gst_code', 'category', 'company']
    search_fields = ['name', 'sku', 'description']
    ordering = ['-created_at']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariantInline]
    
    fieldsets = (
        (None, {
            'fields': ('company', 'category', 'sku', 'barcode', 'name', 'slug')
        }),
        ('Description', {
            'fields': ('short_description', 'description')
        }),
        ('Pricing', {
            'fields': ('base_price', 'cost_price', 'compare_at_price')
        }),
        ('Tax', {
            'fields': ('gst_code', 'gst_rate')
        }),
        ('Inventory', {
            'fields': ('track_inventory', 'allow_backorder', 'low_stock_threshold')
        }),
        ('Physical', {
            'fields': ('weight_grams', 'length_cm', 'width_cm', 'height_cm'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Media & Attributes', {
            'fields': ('images', 'attributes'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """Admin for product variants (standalone)."""
    
    list_display = ['sku', 'product', 'name', 'price_adjustment', 'is_active']
    list_filter = ['is_active', 'product__company']
    search_fields = ['sku', 'name', 'product__name']
    ordering = ['product', 'created_at']


# =============================================================================
# CUSTOMER ADMIN
# =============================================================================

class CustomerAddressInline(admin.TabularInline):
    """Inline for customer addresses."""
    
    model = CustomerAddress
    extra = 0
    fields = [
        'address_type', 'is_default', 'recipient_name', 
        'address_line1', 'postal_code', 'unit_number'
    ]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin for customers."""
    
    list_display = [
        'email', 'first_name', 'last_name', 'customer_type',
        'consent_marketing', 'company'
    ]
    list_filter = ['customer_type', 'consent_marketing', 'company']
    search_fields = ['email', 'first_name', 'last_name', 'company_name']
    ordering = ['-created_at']
    inlines = [CustomerAddressInline]
    
    fieldsets = (
        (None, {
            'fields': ('company', 'user', 'email', 'phone', 'first_name', 'last_name')
        }),
        ('Classification', {
            'fields': ('customer_type', 'tags')
        }),
        ('B2B', {
            'fields': ('company_name', 'company_uen', 'credit_limit', 'credit_used', 'payment_terms'),
            'classes': ('collapse',)
        }),
        ('PDPA Consent', {
            'fields': (
                'consent_marketing', 'consent_analytics',
                'consent_timestamp', 'consent_ip_address', 'data_retention_until'
            )
        }),
        ('Preferences', {
            'fields': ('preferred_language', 'preferred_currency')
        }),
    )
    
    readonly_fields = ['consent_timestamp', 'created_at', 'updated_at']


@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    """Admin for customer addresses (standalone)."""
    
    list_display = ['recipient_name', 'customer', 'address_type', 'postal_code', 'is_default']
    list_filter = ['address_type', 'is_default', 'country']
    search_fields = ['recipient_name', 'address_line1', 'postal_code']
    ordering = ['customer', '-is_default', 'created_at']


# =============================================================================
# CART ADMIN
# =============================================================================

class CartItemInline(admin.TabularInline):
    """Inline for cart items."""
    
    model = CartItem
    extra = 0
    fields = ['product', 'variant', 'quantity', 'unit_price', 'is_saved_for_later']
    readonly_fields = ['unit_price']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin for shopping carts."""
    
    list_display = ['id', 'customer', 'session_id', 'status', 'expires_at', 'company']
    list_filter = ['status', 'company']
    search_fields = ['customer__email', 'session_id']
    ordering = ['-created_at']
    inlines = [CartItemInline]
    
    fieldsets = (
        (None, {
            'fields': ('company', 'customer', 'session_id', 'status', 'expires_at')
        }),
        ('Conversion', {
            'fields': ('converted_order_id', 'converted_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


# =============================================================================
# ORDER ADMIN
# =============================================================================

class OrderItemInline(admin.TabularInline):
    """Inline for order items."""
    
    model = OrderItem
    extra = 0
    fields = [
        'sku', 'name', 'quantity', 'unit_price', 
        'gst_code', 'gst_amount', 'line_total', 'fulfilled_quantity'
    ]
    readonly_fields = ['sku', 'name', 'unit_price', 'gst_code', 'gst_amount', 'line_total']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for orders."""
    
    list_display = [
        'order_number', 'status', 'payment_status', 'fulfillment_status',
        'total_amount', 'order_date', 'company'
    ]
    list_filter = ['status', 'payment_status', 'fulfillment_status', 'company']
    search_fields = ['order_number', 'customer__email']
    ordering = ['-order_date']
    date_hierarchy = 'order_date'
    inlines = [OrderItemInline]
    
    fieldsets = (
        (None, {
            'fields': ('company', 'customer', 'order_number')
        }),
        ('Status', {
            'fields': ('status', 'payment_status', 'fulfillment_status')
        }),
        ('Amounts', {
            'fields': (
                'subtotal', 'discount_amount', 'shipping_amount',
                'gst_amount', 'total_amount', 'currency'
            )
        }),
        ('GST Reporting', {
            'fields': ('gst_box_1_amount', 'gst_box_6_amount'),
            'classes': ('collapse',)
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_reference', 'paid_at')
        }),
        ('Shipping', {
            'fields': (
                'shipping_method', 'shipping_address', 'billing_address',
                'tracking_number', 'carrier', 'shipped_at', 'delivered_at'
            )
        }),
        ('Notes', {
            'fields': ('customer_notes', 'internal_notes', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Cancellation', {
            'fields': ('cancelled_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = [
        'order_number', 'subtotal', 'gst_amount', 'total_amount',
        'gst_box_1_amount', 'gst_box_6_amount',
        'paid_at', 'shipped_at', 'delivered_at', 'cancelled_at',
        'created_at', 'updated_at'
    ]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin for order items (standalone)."""
    
    list_display = ['sku', 'name', 'order', 'quantity', 'line_total', 'fulfilled_quantity']
    list_filter = ['gst_code', 'order__company']
    search_fields = ['sku', 'name', 'order__order_number']
    ordering = ['-created_at']
