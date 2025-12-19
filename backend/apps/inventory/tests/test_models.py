"""
Unit tests for inventory models.
"""
import pytest
from decimal import Decimal
from datetime import timedelta

from django.utils import timezone
from django.db import IntegrityError

from apps.inventory.models import (
    Location, InventoryItem, InventoryReservation, InventoryMovement,
)
from apps.inventory.tests.factories import (
    LocationFactory, StoreLocationFactory, InventoryItemFactory,
    LowStockInventoryItemFactory, InventoryReservationFactory,
    InventoryMovementFactory,
)


pytestmark = pytest.mark.django_db


class TestLocationModel:
    """Tests for Location model."""
    
    def test_create_location(self):
        """Test basic location creation."""
        location = LocationFactory()
        assert location.id is not None
        assert location.code
        assert location.location_type == 'warehouse'
        assert location.is_active is True
    
    def test_location_types(self):
        """Test different location types."""
        warehouse = LocationFactory(location_type='warehouse')
        store = StoreLocationFactory()
        virtual = LocationFactory(location_type='virtual')
        
        assert warehouse.location_type == 'warehouse'
        assert store.location_type == 'store'
        assert virtual.location_type == 'virtual'
    
    def test_full_address(self):
        """Test full_address property."""
        location = LocationFactory(
            address_line1='123 Test Street',
            address_line2='Unit 5',
            postal_code='123456'
        )
        assert 'Test Street' in location.full_address
        assert 'Singapore 123456' in location.full_address
    
    def test_code_uniqueness_per_company(self):
        """Test code must be unique within company."""
        loc1 = LocationFactory(code='UNIQUE-CODE')
        with pytest.raises(IntegrityError):
            LocationFactory(company=loc1.company, code='UNIQUE-CODE')
    
    def test_default_location_exclusivity(self):
        """Test only one default location per company."""
        loc1 = LocationFactory(is_default=True)
        loc2 = LocationFactory(company=loc1.company, is_default=True)
        
        loc1.refresh_from_db()
        assert loc1.is_default is False
        assert loc2.is_default is True


class TestInventoryItemModel:
    """Tests for InventoryItem model."""
    
    def test_create_inventory_item(self):
        """Test basic inventory item creation."""
        item = InventoryItemFactory()
        assert item.id is not None
        assert item.available_qty == 100
        assert item.reserved_qty == 0
    
    def test_net_qty_property(self):
        """Test net_qty calculation."""
        item = InventoryItemFactory(available_qty=100, reserved_qty=30)
        assert item.net_qty == 70
    
    def test_is_low_stock(self):
        """Test low stock detection."""
        item = InventoryItemFactory(available_qty=5, reorder_point=10)
        assert item.is_low_stock is True
        
        item.available_qty = 15
        assert item.is_low_stock is False
    
    def test_can_reserve(self):
        """Test reserve capability check."""
        item = InventoryItemFactory(available_qty=10, reserved_qty=5)
        
        assert item.can_reserve(5) is True  # net_qty = 5
        assert item.can_reserve(6) is False
    
    def test_sku_property(self):
        """Test SKU property."""
        item = InventoryItemFactory()
        assert item.sku == item.product.sku
    
    def test_version_increment(self):
        """Test optimistic locking version increment."""
        item = InventoryItemFactory(version=1)
        item.increment_version()
        assert item.version == 2
    
    def test_product_location_combination(self):
        """Test inventory items are tracked per product/location combination."""
        item1 = InventoryItemFactory()
        
        # Different location = OK
        item2 = InventoryItemFactory(
            company=item1.company,
            product=item1.product,
        )
        
        assert item1.location != item2.location  # Factory creates new location


class TestInventoryReservationModel:
    """Tests for InventoryReservation model."""
    
    def test_create_reservation(self):
        """Test basic reservation creation."""
        reservation = InventoryReservationFactory()
        assert reservation.id is not None
        assert reservation.status == 'pending'
        assert reservation.quantity > 0
    
    def test_is_expired(self):
        """Test expiry detection."""
        reservation = InventoryReservationFactory(
            expires_at=timezone.now() + timedelta(hours=1)
        )
        assert reservation.is_expired is False
        
        reservation.expires_at = timezone.now() - timedelta(minutes=5)
        assert reservation.is_expired is True
    
    def test_is_active(self):
        """Test active status."""
        reservation = InventoryReservationFactory()
        assert reservation.is_active is True
        
        reservation.status = 'confirmed'
        assert reservation.is_active is False
    
    def test_confirm_reservation(self):
        """Test confirmation."""
        reservation = InventoryReservationFactory(status='pending')
        reservation.confirm()
        
        assert reservation.status == 'confirmed'
        assert reservation.confirmed_at is not None
    
    def test_confirm_non_pending_raises(self):
        """Test confirming non-pending reservation raises error."""
        reservation = InventoryReservationFactory(status='confirmed')
        with pytest.raises(ValueError):
            reservation.confirm()
    
    def test_release_reservation(self):
        """Test release."""
        reservation = InventoryReservationFactory(status='pending')
        reservation.release()
        
        assert reservation.status == 'released'
        assert reservation.released_at is not None


class TestInventoryMovementModel:
    """Tests for InventoryMovement model."""
    
    def test_create_movement(self):
        """Test basic movement creation."""
        movement = InventoryMovementFactory()
        assert movement.id is not None
        assert movement.movement_type == 'adjustment'
    
    def test_quantity_display(self):
        """Test string representation with +/- quantity."""
        movement = InventoryMovementFactory(quantity=10)
        assert '+10' in str(movement)
        
        movement.quantity = -5
        assert '-5' in str(movement)
    
    def test_immutable_movement(self):
        """Test movements cannot be updated."""
        movement = InventoryMovementFactory()
        movement.notes = "Updated notes"
        
        with pytest.raises(ValueError) as exc:
            movement.save()
        
        assert "immutable" in str(exc.value).lower()
    
    def test_create_movement_factory_method(self):
        """Test factory method for creating movements."""
        item = InventoryItemFactory(available_qty=100)
        
        movement = InventoryMovement.create_movement(
            inventory_item=item,
            movement_type='purchase',
            quantity=50,
            notes='Stock received',
        )
        
        assert movement.quantity == 50
        assert movement.quantity_before == 100
        assert movement.quantity_after == 150
        assert movement.movement_type == 'purchase'
