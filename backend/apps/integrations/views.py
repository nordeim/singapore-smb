"""Integrations API views."""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.integrations.serializers import (
    ShippingRateSerializer, ShipmentSerializer,
    CreateShipmentSerializer, TrackingEventSerializer,
)
from apps.integrations.services import ShippingService


class ShippingRatesView(APIView):
    """Get shipping rates for an order."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, order_id):
        from apps.commerce.models import Order
        
        try:
            order = Order.objects.get(
                id=order_id,
                company=request.user.company,
            )
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        rates = ShippingService.get_rates_for_order(order)
        
        return Response({
            'rates': ShippingRateSerializer(rates, many=True).data
        })


class CreateShipmentView(APIView):
    """Create a shipment for an order."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = CreateShipmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from apps.commerce.models import Order
        
        try:
            order = Order.objects.get(
                id=serializer.validated_data['order_id'],
                company=request.user.company,
            )
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            shipment = ShippingService.create_shipment(
                order=order,
                rate_id=serializer.validated_data['rate_id'],
            )
            
            return Response(
                ShipmentSerializer(shipment).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TrackingView(APIView):
    """Get tracking for a shipment."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, tracking_number):
        carrier = request.query_params.get('carrier')
        
        events = ShippingService.get_tracking(
            tracking_number=tracking_number,
            carrier=carrier,
        )
        
        return Response({
            'tracking_number': tracking_number,
            'events': TrackingEventSerializer(events, many=True).data
        })
