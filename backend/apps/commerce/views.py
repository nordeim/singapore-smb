"""
DRF ViewSets for commerce domain.

Implements ViewSets with:
- Company-scoped filtering
- Permission checks
- Custom actions for status transitions
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from core.permissions import IsCompanyMember
from apps.commerce.models import (
    Category, Product, ProductVariant,
    Customer, CustomerAddress,
    Cart, CartItem, Order, OrderItem,
)
from apps.commerce.serializers import (
    CategorySerializer, CategoryTreeSerializer,
    ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer,
    ProductVariantSerializer,
    CustomerSerializer, CustomerAddressSerializer,
    CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer,
    OrderListSerializer, OrderDetailSerializer, OrderCreateSerializer,
    ShipOrderSerializer, CancelOrderSerializer,
)
from apps.commerce.services import ProductService, CartService, OrderService


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for product categories."""
    
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['parent', 'is_active']
    search_fields = ['name', 'slug']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['sort_order', 'name']
    
    def get_queryset(self):
        """Filter categories by user's company."""
        return Category.objects.filter(company=self.request.user.company)
    
    def perform_create(self, serializer):
        """Set company on create."""
        serializer.save(company=self.request.user.company)
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get category tree structure."""
        root_categories = self.get_queryset().filter(parent__isnull=True, is_active=True)
        serializer = CategoryTreeSerializer(root_categories, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for products."""
    
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'status', 'gst_code']
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'base_price', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter products by user's company."""
        return Product.objects.filter(company=self.request.user.company)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer
    
    def perform_create(self, serializer):
        """Set company on create."""
        serializer.save(company=self.request.user.company)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Full-text search products."""
        query = request.query_params.get('q', '')
        category_id = request.query_params.get('category')
        status_filter = request.query_params.get('status')
        
        products = ProductService.search(
            company=request.user.company,
            query=query,
            category_id=category_id,
            status=status_filter
        )
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for customers."""
    
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['customer_type']
    search_fields = ['email', 'first_name', 'last_name', 'company_name']
    ordering_fields = ['created_at', 'email', 'last_name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter customers by user's company."""
        return Customer.objects.filter(company=self.request.user.company)
    
    def perform_create(self, serializer):
        """Set company on create."""
        serializer.save(company=self.request.user.company)
    
    @action(detail=True, methods=['get'])
    def addresses(self, request, pk=None):
        """Get customer addresses."""
        customer = self.get_object()
        serializer = CustomerAddressSerializer(customer.addresses.all(), many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_address(self, request, pk=None):
        """Add address to customer."""
        customer = self.get_object()
        serializer = CustomerAddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=customer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def pdpa_export(self, request, pk=None):
        """Export customer data for PDPA compliance."""
        customer = self.get_object()
        # Include all customer data and related orders
        data = {
            'customer': CustomerSerializer(customer).data,
            'orders': OrderListSerializer(customer.orders.all()[:50], many=True).data,
        }
        return Response(data)


class CartViewSet(viewsets.GenericViewSet):
    """ViewSet for shopping carts."""
    
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    
    def get_queryset(self):
        """Filter carts by user's company."""
        return Cart.objects.filter(company=self.request.user.company)
    
    def get_cart(self, request):
        """Get or create cart for current user/session."""
        # Try to get customer for logged-in user
        customer = None
        if hasattr(request.user, 'customer_profiles'):
            customer = request.user.customer_profiles.filter(
                company=request.user.company
            ).first()
        
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        return CartService.get_or_create_cart(
            company=request.user.company,
            customer=customer,
            session_id=session_id if not customer else None
        )
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current cart."""
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart."""
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cart = self.get_cart(request)
        
        product = Product.objects.get(
            id=serializer.validated_data['product_id'],
            company=request.user.company
        )
        
        variant = None
        variant_id = serializer.validated_data.get('variant_id')
        if variant_id:
            variant = ProductVariant.objects.get(id=variant_id, product=product)
        
        cart_item = CartService.add_item(
            cart=cart,
            product=product,
            variant=variant,
            quantity=serializer.validated_data.get('quantity', 1)
        )
        
        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], url_path='update_item/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        """Update cart item quantity."""
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cart = self.get_cart(request)
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        
        CartService.update_item_quantity(
            cart_item=cart_item,
            quantity=serializer.validated_data['quantity']
        )
        
        return Response(CartItemSerializer(cart_item).data)
    
    @action(detail=False, methods=['delete'], url_path='remove_item/(?P<item_id>[^/.]+)')
    def remove_item(self, request, item_id=None):
        """Remove item from cart."""
        cart = self.get_cart(request)
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        CartService.remove_item(cart_item)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """Checkout cart to create order."""
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cart = Cart.objects.get(
            id=serializer.validated_data['cart_id'],
            company=request.user.company
        )
        
        # Get addresses
        shipping_address = serializer.validated_data.get('shipping_address')
        billing_address = serializer.validated_data.get('billing_address')
        
        # If address IDs provided, load from customer
        if not shipping_address and cart.customer:
            shipping_addr_id = serializer.validated_data.get('shipping_address_id')
            if shipping_addr_id:
                addr = CustomerAddress.objects.get(
                    id=shipping_addr_id, customer=cart.customer
                )
                shipping_address = addr.to_dict()
        
        order = CartService.checkout(
            cart=cart,
            shipping_address=shipping_address or {},
            billing_address=billing_address,
            payment_method=serializer.validated_data.get('payment_method', ''),
            shipping_method=serializer.validated_data.get('shipping_method', ''),
            customer_notes=serializer.validated_data.get('customer_notes', '')
        )
        
        return Response(OrderDetailSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for orders."""
    
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'payment_status', 'fulfillment_status', 'customer']
    search_fields = ['order_number']
    ordering_fields = ['order_date', 'total_amount', 'created_at']
    ordering = ['-order_date']
    
    def get_queryset(self):
        """Filter orders by user's company."""
        return Order.objects.filter(company=self.request.user.company)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return OrderListSerializer
        return OrderDetailSerializer
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm an order."""
        order = self.get_object()
        try:
            OrderService.confirm(order)
            return Response(OrderDetailSerializer(order).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Start processing an order."""
        order = self.get_object()
        try:
            OrderService.process(order)
            return Response(OrderDetailSerializer(order).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        """Ship an order."""
        order = self.get_object()
        serializer = ShipOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            OrderService.ship(
                order,
                tracking_number=serializer.validated_data.get('tracking_number', ''),
                carrier=serializer.validated_data.get('carrier', '')
            )
            return Response(OrderDetailSerializer(order).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def deliver(self, request, pk=None):
        """Mark order as delivered."""
        order = self.get_object()
        try:
            OrderService.deliver(order)
            return Response(OrderDetailSerializer(order).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order."""
        order = self.get_object()
        serializer = CancelOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            OrderService.cancel(order, reason=serializer.validated_data.get('reason', ''))
            return Response(OrderDetailSerializer(order).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
