"""
Django admin configuration for inventory models.
"""
from django.contrib import admin
from django.utils.html import format_html

from apps.inventory.models import (
    Location, InventoryItem, InventoryReservation, InventoryMovement,
)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Admin for inventory locations."""
    
    list_display = ['code', 'name', 'location_type', 'is_active', 'is_default', 'company']
    list_filter = ['location_type', 'is_active', 'is_default', 'company']
    search_fields = ['code', 'name']
    ordering = ['company', 'code']
    
    fieldsets = (
        (None, {
            'fields': ('company', 'code', 'name', 'location_type')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'postal_code'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_default')
        }),
        ('Settings', {
            'fields': ('settings',),
            'classes': ('collapse',)
        }),
    )


class InventoryReservationInline(admin.TabularInline):
    """Inline for inventory reservations."""
    
    model = InventoryReservation
    extra = 0
    readonly_fields = ['id', 'order_id', 'quantity', 'status', 'expires_at', 'created_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    """Admin for inventory items."""
    
    list_display = [
        'sku', 'product', 'location', 'available_qty', 'reserved_qty',
        'net_qty_display', 'low_stock_indicator', 'version'
    ]
    list_filter = ['location', 'product__category', 'company']
    search_fields = ['product__name', 'product__sku', 'variant__sku']
    ordering = ['product__name', 'location__code']
    inlines = [InventoryReservationInline]
    
    fieldsets = (
        (None, {
            'fields': ('company', 'product', 'variant', 'location')
        }),
        ('Quantities', {
            'fields': ('available_qty', 'reserved_qty')
        }),
        ('Reorder Settings', {
            'fields': ('reorder_point', 'reorder_quantity'),
            'classes': ('collapse',)
        }),
        ('Costing', {
            'fields': ('unit_cost',),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('last_counted_at', 'last_movement_at', 'version'),
        }),
    )
    
    readonly_fields = ['last_movement_at', 'version']
    
    @admin.display(description='Net Qty')
    def net_qty_display(self, obj):
        """Display net quantity."""
        return obj.net_qty
    
    @admin.display(description='Low Stock')
    def low_stock_indicator(self, obj):
        """Display low stock indicator with color."""
        if obj.is_low_stock:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠ LOW</span>'
            )
        return format_html('<span style="color: green;">✓ OK</span>')


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    """Admin for inventory movements (read-only audit log)."""
    
    list_display = [
        'created_at', 'movement_type', 'quantity_display',
        'inventory_item', 'quantity_before', 'quantity_after',
        'created_by'
    ]
    list_filter = ['movement_type', 'company', 'created_at']
    search_fields = ['inventory_item__product__name', 'notes']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    readonly_fields = [
        'id', 'company', 'inventory_item', 'movement_type',
        'quantity', 'quantity_before', 'quantity_after',
        'reference_type', 'reference_id', 'notes',
        'created_at', 'created_by',
    ]
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    @admin.display(description='Quantity')
    def quantity_display(self, obj):
        """Display quantity with color coding."""
        if obj.quantity > 0:
            return format_html(
                '<span style="color: green;">+{}</span>',
                obj.quantity
            )
        else:
            return format_html(
                '<span style="color: red;">{}</span>',
                obj.quantity
            )


@admin.register(InventoryReservation)
class InventoryReservationAdmin(admin.ModelAdmin):
    """Admin for inventory reservations."""
    
    list_display = [
        'id', 'inventory_item', 'order_id', 'quantity',
        'status', 'expires_at', 'is_expired_display'
    ]
    list_filter = ['status', 'inventory_item__company']
    search_fields = ['order_id', 'inventory_item__product__name']
    ordering = ['-created_at']
    
    readonly_fields = [
        'id', 'inventory_item', 'order_id', 'quantity',
        'status', 'expires_at', 'confirmed_at', 'released_at', 'created_at',
    ]
    
    def has_add_permission(self, request):
        return False
    
    @admin.display(description='Expired')
    def is_expired_display(self, obj):
        """Display expired status."""
        if obj.is_expired:
            return format_html('<span style="color: red;">Yes</span>')
        return 'No'
