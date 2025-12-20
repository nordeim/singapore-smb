"""Integrations serializers."""
from rest_framework import serializers
from decimal import Decimal


class ShippingRateSerializer(serializers.Serializer):
    """Serializer for shipping rates."""
    
    provider = serializers.CharField()
    service_type = serializers.CharField()
    service_name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField()
    estimated_days = serializers.IntegerField()
    rate_id = serializers.CharField()


class ShipmentSerializer(serializers.Serializer):
    """Serializer for shipments."""
    
    id = serializers.CharField()
    tracking_number = serializers.CharField()
    provider = serializers.CharField()
    service_type = serializers.CharField()
    status = serializers.CharField()
    label_url = serializers.URLField(required=False, allow_null=True)


class CreateShipmentSerializer(serializers.Serializer):
    """Serializer for creating shipments."""
    
    order_id = serializers.UUIDField()
    rate_id = serializers.CharField()


class TrackingEventSerializer(serializers.Serializer):
    """Serializer for tracking events."""
    
    timestamp = serializers.CharField()
    status = serializers.CharField()
    location = serializers.CharField()
    description = serializers.CharField()
    carrier = serializers.CharField(required=False)
