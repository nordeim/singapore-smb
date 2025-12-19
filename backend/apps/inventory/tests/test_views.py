"""
API integration tests for inventory views.
"""
import pytest
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.inventory.models import Location, InventoryItem
from apps.inventory.tests.factories import (
    LocationFactory, InventoryItemFactory, LowStockInventoryItemFactory,
)
from apps.accounts.tests.factories import CompanyFactory, UserFactory


pytestmark = pytest.mark.django_db


class TestLocationViewSet:
    """Tests for LocationViewSet."""
    
    def setup_method(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company)
        self.client.force_authenticate(user=self.user)
    
    def test_list_locations(self):
        """Test listing locations."""
        LocationFactory(company=self.company)
        LocationFactory(company=self.company)
        
        response = self.client.get('/api/v1/inventory/locations/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_create_location(self):
        """Test creating a location."""
        data = {
            'code': 'WH-TEST',
            'name': 'Test Warehouse',
            'location_type': 'warehouse',
            'is_active': True,
        }
        
        response = self.client.post('/api/v1/inventory/locations/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['code'] == 'WH-TEST'
    
    def test_company_isolation(self):
        """Test that locations from other companies are not visible."""
        other_company = CompanyFactory()
        LocationFactory(company=other_company)
        my_location = LocationFactory(company=self.company)
        
        response = self.client.get('/api/v1/inventory/locations/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == str(my_location.id)


class TestInventoryItemViewSet:
    """Tests for InventoryItemViewSet."""
    
    def setup_method(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company)
        self.client.force_authenticate(user=self.user)
    
    def test_list_inventory_items(self):
        """Test listing inventory items."""
        location = LocationFactory(company=self.company)
        InventoryItemFactory(company=self.company, location=location)
        InventoryItemFactory(company=self.company, location=location)
        
        response = self.client.get('/api/v1/inventory/items/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_adjust_stock_increase(self):
        """Test stock adjustment (increase)."""
        location = LocationFactory(company=self.company)
        item = InventoryItemFactory(
            company=self.company,
            location=location,
            available_qty=100
        )
        
        data = {'quantity': 50, 'notes': 'Stock received'}
        
        response = self.client.post(f'/api/v1/inventory/items/{item.id}/adjust/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['available_qty'] == 150
    
    def test_adjust_stock_decrease(self):
        """Test stock adjustment (decrease)."""
        location = LocationFactory(company=self.company)
        item = InventoryItemFactory(
            company=self.company,
            location=location,
            available_qty=100,
            reserved_qty=0
        )
        
        data = {'quantity': -30, 'notes': 'Damaged'}
        
        response = self.client.post(f'/api/v1/inventory/items/{item.id}/adjust/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['available_qty'] == 70
    
    def test_adjust_stock_invalid(self):
        """Test invalid stock adjustment."""
        location = LocationFactory(company=self.company)
        item = InventoryItemFactory(
            company=self.company,
            location=location,
            available_qty=10
        )
        
        data = {'quantity': -50, 'notes': 'Too much'}
        
        response = self.client.post(f'/api/v1/inventory/items/{item.id}/adjust/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_low_stock_action(self):
        """Test low stock endpoint."""
        location = LocationFactory(company=self.company)
        LowStockInventoryItemFactory(company=self.company, location=location)
        InventoryItemFactory(company=self.company, location=location)  # Normal stock
        
        response = self.client.get('/api/v1/inventory/items/low_stock/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
    
    def test_receive_stock(self):
        """Test stock receive action."""
        location = LocationFactory(company=self.company)
        item = InventoryItemFactory(
            company=self.company,
            location=location,
            available_qty=100
        )
        
        data = {
            'quantity': 25,
            'unit_cost': '12.50',
            'notes': 'PO-12345',
        }
        
        response = self.client.post(f'/api/v1/inventory/items/{item.id}/receive/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['available_qty'] == 125


class TestInventoryMovementViewSet:
    """Tests for InventoryMovementViewSet."""
    
    def setup_method(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company)
        self.client.force_authenticate(user=self.user)
    
    def test_list_movements(self):
        """Test listing movements (read-only)."""
        # Create an adjustment to generate a movement
        location = LocationFactory(company=self.company)
        item = InventoryItemFactory(company=self.company, location=location)
        
        from apps.inventory.services import InventoryService
        InventoryService.adjust_stock(item, 10, 'Test adjustment')
        
        response = self.client.get('/api/v1/inventory/movements/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
    
    def test_movements_read_only(self):
        """Test that movements cannot be created via API."""
        response = self.client.post('/api/v1/inventory/movements/', {})
        
        # Should be 405 Method Not Allowed (read-only viewset)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
