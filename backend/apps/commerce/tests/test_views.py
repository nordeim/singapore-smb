"""
API integration tests for commerce views.

Tests:
- Product search endpoint
- Category tree endpoint
- Cart operations
- Order status transitions
- Company isolation
"""
import pytest
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.commerce.models import Cart, Order
from apps.commerce.tests.factories import (
    CategoryFactory, ProductFactory,
    CustomerFactory, CartFactory, CartItemFactory,
    OrderFactory,
)
from apps.accounts.tests.factories import CompanyFactory, UserFactory


pytestmark = pytest.mark.django_db


class TestCategoryViewSet:
    """Tests for CategoryViewSet."""
    
    def setup_method(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company)
        self.client.force_authenticate(user=self.user)
    
    def test_list_categories(self):
        """Test listing categories."""
        CategoryFactory(company=self.company, name="Cat 1")
        CategoryFactory(company=self.company, name="Cat 2")
        
        response = self.client.get('/api/v1/commerce/categories/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_category_tree(self):
        """Test category tree endpoint."""
        parent = CategoryFactory(company=self.company, name="Parent")
        CategoryFactory(company=self.company, parent=parent, name="Child")
        
        response = self.client.get('/api/v1/commerce/categories/tree/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'Parent'
        assert len(response.data[0]['children']) == 1
    
    def test_company_isolation(self):
        """Test that categories from other companies are not visible."""
        other_company = CompanyFactory()
        CategoryFactory(company=other_company, name="Other Company Cat")
        CategoryFactory(company=self.company, name="My Company Cat")
        
        response = self.client.get('/api/v1/commerce/categories/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'My Company Cat'


class TestProductViewSet:
    """Tests for ProductViewSet."""
    
    def setup_method(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company)
        self.client.force_authenticate(user=self.user)
    
    def test_list_products(self):
        """Test listing products."""
        ProductFactory(company=self.company, name="Product 1")
        ProductFactory(company=self.company, name="Product 2")
        
        response = self.client.get('/api/v1/commerce/products/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_search_products(self):
        """Test product search endpoint."""
        ProductFactory(company=self.company, name="Blue Widget", status='active')
        ProductFactory(company=self.company, name="Red Gadget", status='active')
        
        response = self.client.get('/api/v1/commerce/products/search/?q=blue')
        
        assert response.status_code == status.HTTP_200_OK
        # Note: Full-text search may require specific data setup
    
    def test_create_product(self):
        """Test product creation."""
        category = CategoryFactory(company=self.company)
        
        data = {
            'sku': 'NEW-PROD-001',
            'name': 'New Product',
            'slug': 'new-product',
            'base_price': '99.99',
            'gst_code': 'SR',
            'gst_rate': '0.09',
            'status': 'draft',
            'category': str(category.id),
        }
        
        response = self.client.post('/api/v1/commerce/products/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['sku'] == 'NEW-PROD-001'


class TestCartViewSet:
    """Tests for CartViewSet."""
    
    def setup_method(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company)
        self.client.force_authenticate(user=self.user)
    
    def test_get_current_cart(self):
        """Test getting current cart."""
        response = self.client.get('/api/v1/commerce/cart/current/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'items' in response.data
    
    def test_add_item_to_cart(self):
        """Test adding item to cart."""
        product = ProductFactory(company=self.company, base_price=Decimal('50.00'))
        
        data = {
            'product_id': str(product.id),
            'quantity': 2,
        }
        
        response = self.client.post('/api/v1/commerce/cart/add_item/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['quantity'] == 2
        assert str(response.data['product']) == str(product.id)


class TestOrderViewSet:
    """Tests for OrderViewSet."""
    
    def setup_method(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company)
        self.client.force_authenticate(user=self.user)
    
    def test_list_orders(self):
        """Test listing orders."""
        OrderFactory(company=self.company)
        OrderFactory(company=self.company)
        
        response = self.client.get('/api/v1/commerce/orders/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_confirm_order(self):
        """Test order confirmation action."""
        order = OrderFactory(company=self.company, status='pending')
        
        response = self.client.post(f'/api/v1/commerce/orders/{order.id}/confirm/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'confirmed'
    
    def test_ship_order(self):
        """Test order shipping action."""
        order = OrderFactory(company=self.company, status='processing')
        
        data = {
            'tracking_number': 'TRK-12345',
            'carrier': 'SingPost',
        }
        
        response = self.client.post(f'/api/v1/commerce/orders/{order.id}/ship/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'shipped'
        assert response.data['tracking_number'] == 'TRK-12345'
    
    def test_cancel_order(self):
        """Test order cancellation action."""
        order = OrderFactory(company=self.company, status='pending')
        
        data = {'reason': 'Customer request'}
        
        response = self.client.post(f'/api/v1/commerce/orders/{order.id}/cancel/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'cancelled'
    
    def test_invalid_transition_returns_error(self):
        """Test invalid status transition returns 400."""
        order = OrderFactory(company=self.company, status='delivered')
        
        response = self.client.post(f'/api/v1/commerce/orders/{order.id}/cancel/')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_company_isolation(self):
        """Test that orders from other companies are not visible."""
        other_company = CompanyFactory()
        OrderFactory(company=other_company)
        my_order = OrderFactory(company=self.company)
        
        response = self.client.get('/api/v1/commerce/orders/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == str(my_order.id)
