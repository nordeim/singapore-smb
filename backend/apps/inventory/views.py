"""
DRF ViewSets for inventory domain.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from core.permissions import IsCompanyMember
from apps.inventory.models import (
    Location, InventoryItem, InventoryReservation, InventoryMovement,
)
from apps.inventory.serializers import (
    LocationSerializer, LocationListSerializer,
    InventoryItemSerializer, InventoryItemDetailSerializer,
    StockAdjustmentSerializer, StockTransferSerializer, StockReceiveSerializer,
    StockLevelSerializer,
    InventoryReservationSerializer,
    InventoryMovementSerializer,
)
from apps.inventory.services import InventoryService, InsufficientStockError


class LocationViewSet(viewsets.ModelViewSet):
    """ViewSet for inventory locations."""
    
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['location_type', 'is_active', 'is_default']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name', 'created_at']
    ordering = ['code']
    
    def get_queryset(self):
        """Filter locations by user's company."""
        return Location.objects.filter(company=self.request.user.company)
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'list':
            return LocationListSerializer
        return LocationSerializer
    
    def perform_create(self, serializer):
        """Set company on create."""
        serializer.save(company=self.request.user.company)


class InventoryItemViewSet(viewsets.ModelViewSet):
    """ViewSet for inventory items."""
    
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['location', 'product']
    search_fields = ['product__name', 'product__sku']
    ordering_fields = ['product__name', 'available_qty', 'created_at']
    ordering = ['product__name']
    
    def get_queryset(self):
        """Filter items by user's company."""
        return InventoryItem.objects.filter(
            company=self.request.user.company
        ).select_related('product', 'variant', 'location')
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'retrieve':
            return InventoryItemDetailSerializer
        return InventoryItemSerializer
    
    def perform_create(self, serializer):
        """Set company on create."""
        serializer.save(company=self.request.user.company)
    
    @action(detail=True, methods=['post'])
    def adjust(self, request, pk=None):
        """Adjust stock level."""
        item = self.get_object()
        serializer = StockAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            movement = InventoryService.adjust_stock(
                inventory_item=item,
                quantity_delta=serializer.validated_data['quantity'],
                notes=serializer.validated_data.get('notes', ''),
                user=request.user,
            )
            
            # Refresh and return updated item
            item.refresh_from_db()
            return Response(InventoryItemSerializer(item).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def transfer(self, request, pk=None):
        """Transfer stock to another location."""
        from_item = self.get_object()
        serializer = StockTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get or create destination item
        to_location_id = serializer.validated_data['to_location_id']
        to_location = Location.objects.get(
            id=to_location_id,
            company=request.user.company
        )
        
        to_item, _ = InventoryItem.objects.get_or_create(
            company=request.user.company,
            product=from_item.product,
            variant=from_item.variant,
            location=to_location,
            defaults={'available_qty': 0, 'reserved_qty': 0}
        )
        
        try:
            InventoryService.transfer_stock(
                from_item=from_item,
                to_item=to_item,
                quantity=serializer.validated_data['quantity'],
                notes=serializer.validated_data.get('notes', ''),
                user=request.user,
            )
            
            # Return both items
            from_item.refresh_from_db()
            to_item.refresh_from_db()
            return Response({
                'from_item': InventoryItemSerializer(from_item).data,
                'to_item': InventoryItemSerializer(to_item).data,
            })
        except InsufficientStockError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        """Receive stock (purchase)."""
        item = self.get_object()
        serializer = StockReceiveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        InventoryService.receive_stock(
            inventory_item=item,
            quantity=serializer.validated_data['quantity'],
            unit_cost=serializer.validated_data.get('unit_cost'),
            notes=serializer.validated_data.get('notes', ''),
            reference_id=serializer.validated_data.get('reference_id'),
            user=request.user,
        )
        
        item.refresh_from_db()
        return Response(InventoryItemSerializer(item).data)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get items with low stock."""
        items = InventoryService.check_low_stock(company=request.user.company)
        serializer = InventoryItemSerializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stock_levels(self, request, pk=None):
        """Get aggregated stock levels for this product."""
        item = self.get_object()
        levels = InventoryService.get_stock_levels(
            product=item.product,
            company=request.user.company
        )
        serializer = StockLevelSerializer(data=levels)
        serializer.is_valid()
        return Response(levels)


class InventoryMovementViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for inventory movements (read-only audit log)."""
    
    serializer_class = InventoryMovementSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['inventory_item', 'movement_type']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter movements by user's company."""
        return InventoryMovement.objects.filter(
            company=self.request.user.company
        ).select_related('inventory_item', 'inventory_item__location', 'created_by')


class InventoryReservationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for inventory reservations (read-only for admin)."""
    
    serializer_class = InventoryReservationSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'inventory_item']
    ordering_fields = ['created_at', 'expires_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter reservations by user's company."""
        return InventoryReservation.objects.filter(
            inventory_item__company=self.request.user.company
        ).select_related('inventory_item')
    
    @action(detail=False, methods=['post'])
    def cleanup(self, request):
        """Manually trigger expired reservation cleanup."""
        count = InventoryService.cleanup_expired_reservations(
            company=request.user.company
        )
        return Response({'expired_count': count})
