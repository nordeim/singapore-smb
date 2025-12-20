"""
Payments API views.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.payments.serializers import (
    PaymentIntentCreateSerializer, PaymentIntentResponseSerializer,
    PaymentMethodSerializer, PaymentStatusSerializer,
)
from apps.payments.services import PaymentOrchestrator
from apps.payments.exceptions import PaymentError


class CreatePaymentIntentView(APIView):
    """
    Create a payment intent for an order.
    
    POST /api/v1/payments/create-intent/
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = PaymentIntentCreateSerializer(data=request.data)
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
            intent = PaymentOrchestrator.create_payment_intent(
                order=order,
                payment_method=serializer.validated_data['payment_method'],
                redirect_url=serializer.validated_data.get('redirect_url'),
            )
            
            return Response(PaymentIntentResponseSerializer(intent).data)
            
        except PaymentError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentMethodsView(APIView):
    """
    Get available payment methods.
    
    GET /api/v1/payments/methods/
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        methods = PaymentOrchestrator.get_available_methods(
            company=request.user.company
        )
        
        return Response({'methods': methods})


class PaymentStatusView(APIView):
    """
    Get payment status for an order.
    
    GET /api/v1/payments/status/{order_id}/
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, order_id):
        from apps.commerce.models import Order
        from apps.accounting.models import Payment
        
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
        
        # Check for payment
        payment = Payment.objects.filter(
            company=order.company,
        ).filter(
            gateway_reference__icontains=str(order.id)
        ).first()
        
        if payment:
            return Response({
                'order_id': str(order.id),
                'payment_status': payment.status,
                'payment_id': str(payment.id),
                'amount_paid': str(payment.amount),
            })
        else:
            return Response({
                'order_id': str(order.id),
                'payment_status': 'pending',
                'payment_id': None,
                'amount_paid': None,
            })
