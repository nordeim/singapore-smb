"""
Payments serializers.
"""
from rest_framework import serializers
from decimal import Decimal


class PaymentIntentCreateSerializer(serializers.Serializer):
    """Serializer for creating payment intents."""
    
    order_id = serializers.UUIDField()
    payment_method = serializers.ChoiceField(choices=[
        'card', 'apple_pay', 'google_pay',
        'paynow', 'grabpay', 'shopee_pay',
    ])
    redirect_url = serializers.URLField(required=False)


class PaymentIntentResponseSerializer(serializers.Serializer):
    """Serializer for payment intent response."""
    
    id = serializers.CharField()
    client_secret = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField()
    status = serializers.CharField()
    gateway = serializers.CharField()
    payment_url = serializers.URLField(required=False, allow_null=True)


class PaymentMethodSerializer(serializers.Serializer):
    """Serializer for available payment methods."""
    
    methods = serializers.ListField(child=serializers.CharField())


class PaymentStatusSerializer(serializers.Serializer):
    """Serializer for payment status response."""
    
    order_id = serializers.UUIDField()
    payment_status = serializers.CharField()
    payment_id = serializers.UUIDField(required=False, allow_null=True)
    amount_paid = serializers.DecimalField(
        max_digits=12, decimal_places=2,
        required=False
    )
