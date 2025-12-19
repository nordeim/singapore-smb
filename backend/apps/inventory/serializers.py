"""
DRF serializers for inventory domain.
"""
from rest_framework import serializers

from apps.inventory.models import (
    Location, InventoryItem, InventoryReservation, InventoryMovement,
    LOCATION_TYPE_CHOICES, RESERVATION_STATUS_CHOICES, MOVEMENT_TYPE_CHOICES,
)


# =============================================================================
# LOCATION SERIALIZERS
# =============================================================================

class LocationSerializer(serializers.ModelSerializer):
    """Full serializer for Location CRUD."""
    
    full_address = serializers.CharField(read_only=True)
    
    class Meta:
        model = Location
        fields = [
            'id', 'code', 'name', 'location_type',
            'address_line1', 'address_line2', 'postal_code',
            'is_active', 'is_default', 'settings',
            'full_address',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_postal_code(self, value):
        """Validate Singapore postal code format."""
        if value and (len(value) != 6 or not value.isdigit()):
            raise serializers.ValidationError(
                "Singapore postal code must be exactly 6 digits"
            )
        return value


class LocationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for location lists."""
    
    class Meta:
        model = Location
        fields = ['id', 'code', 'name', 'location_type', 'is_active', 'is_default']


# =============================================================================
# INVENTORY ITEM SERIALIZERS
# =============================================================================

class InventoryItemSerializer(serializers.ModelSerializer):
    """Full serializer for InventoryItem."""
    
    net_qty = serializers.IntegerField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    sku = serializers.CharField(read_only=True)
    location_code = serializers.CharField(source='location.code', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'product', 'variant', 'location',
            'sku', 'product_name', 'location_code',
            'available_qty', 'reserved_qty', 'net_qty',
            'reorder_point', 'reorder_quantity', 'unit_cost',
            'is_low_stock',
            'last_counted_at', 'last_movement_at',
            'version',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'net_qty', 'is_low_stock', 'sku',
            'last_movement_at', 'version',
            'created_at', 'updated_at',
        ]


class InventoryItemDetailSerializer(InventoryItemSerializer):
    """Detailed serializer with nested location and product info."""
    
    location = LocationListSerializer(read_only=True)
    
    class Meta(InventoryItemSerializer.Meta):
        pass


class StockAdjustmentSerializer(serializers.Serializer):
    """Serializer for stock adjustment action."""
    
    quantity = serializers.IntegerField(
        help_text="Quantity to adjust (+/- for increase/decrease)"
    )
    notes = serializers.CharField(
        max_length=500,
        required=False,
        default='',
        help_text="Reason for adjustment"
    )


class StockTransferSerializer(serializers.Serializer):
    """Serializer for stock transfer action."""
    
    to_location_id = serializers.UUIDField(
        help_text="Destination location ID"
    )
    quantity = serializers.IntegerField(
        min_value=1,
        help_text="Quantity to transfer"
    )
    notes = serializers.CharField(
        max_length=500,
        required=False,
        default='',
        help_text="Transfer notes"
    )


class StockReceiveSerializer(serializers.Serializer):
    """Serializer for stock receive action."""
    
    quantity = serializers.IntegerField(
        min_value=1,
        help_text="Quantity received"
    )
    unit_cost = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="Unit cost for this receipt"
    )
    notes = serializers.CharField(
        max_length=500,
        required=False,
        default='',
        help_text="Receipt notes"
    )
    reference_id = serializers.UUIDField(
        required=False,
        help_text="Optional purchase order reference"
    )


class StockLevelSerializer(serializers.Serializer):
    """Serializer for aggregated stock levels."""
    
    product_id = serializers.UUIDField()
    product_sku = serializers.CharField()
    total_available = serializers.IntegerField()
    total_reserved = serializers.IntegerField()
    total_net = serializers.IntegerField()
    by_location = serializers.ListField(child=serializers.DictField())


# =============================================================================
# RESERVATION SERIALIZERS
# =============================================================================

class InventoryReservationSerializer(serializers.ModelSerializer):
    """Serializer for InventoryReservation (mostly read-only)."""
    
    is_expired = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    item_sku = serializers.CharField(source='inventory_item.sku', read_only=True)
    
    class Meta:
        model = InventoryReservation
        fields = [
            'id', 'inventory_item', 'item_sku', 'order_id',
            'quantity', 'status', 'expires_at',
            'confirmed_at', 'released_at',
            'is_expired', 'is_active',
            'created_at',
        ]
        read_only_fields = [
            'id', 'status', 'expires_at',
            'confirmed_at', 'released_at',
            'is_expired', 'is_active', 'created_at',
        ]


# =============================================================================
# MOVEMENT SERIALIZERS
# =============================================================================

class InventoryMovementSerializer(serializers.ModelSerializer):
    """Serializer for InventoryMovement (read-only audit log)."""
    
    item_sku = serializers.CharField(source='inventory_item.sku', read_only=True)
    location_code = serializers.CharField(
        source='inventory_item.location.code', read_only=True
    )
    created_by_email = serializers.CharField(
        source='created_by.email', read_only=True
    )
    
    class Meta:
        model = InventoryMovement
        fields = [
            'id', 'inventory_item', 'item_sku', 'location_code',
            'movement_type', 'quantity',
            'quantity_before', 'quantity_after',
            'reference_type', 'reference_id',
            'notes',
            'created_at', 'created_by', 'created_by_email',
        ]
        read_only_fields = fields  # All fields read-only
