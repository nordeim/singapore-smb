"""
Unit tests for inventory services.
"""
import uuid
import pytest
from decimal import Decimal
from datetime import timedelta
from unittest.mock import patch, MagicMock

from django.utils import timezone

from apps.inventory.models import InventoryItem, InventoryReservation, InventoryMovement
from apps.inventory.services import InventoryService, InsufficientStockError
from apps.inventory.tests.factories import (
    LocationFactory, InventoryItemFactory, InventoryReservationFactory,
)
from apps.accounts.tests.factories import CompanyFactory, UserFactory


pytestmark = pytest.mark.django_db


class TestInventoryServiceReservation:
    """Tests for reservation operations."""
    
    def test_reserve_stock_success(self):
        """Test successful stock reservation."""
        item = InventoryItemFactory(available_qty=100, reserved_qty=0)
        
        reservation = InventoryService.reserve_stock(
            inventory_item=item,
            quantity=10,
            order_id=str(uuid.uuid4()),
            expires_minutes=30,
        )
        
        assert reservation.quantity == 10
        assert reservation.status == 'pending'
        
        item.refresh_from_db()
        assert item.reserved_qty == 10
        assert item.net_qty == 90
    
    def test_reserve_stock_insufficient(self):
        """Test reservation with insufficient stock."""
        item = InventoryItemFactory(available_qty=5, reserved_qty=0)
        
        with pytest.raises(InsufficientStockError):
            InventoryService.reserve_stock(
                inventory_item=item,
                quantity=10,
                order_id=str(uuid.uuid4()),
            )
    
    def test_reserve_stock_with_existing_reservation(self):
        """Test reservation when some stock already reserved."""
        item = InventoryItemFactory(available_qty=20, reserved_qty=10)
        
        # net_qty = 10, can reserve up to 10
        reservation = InventoryService.reserve_stock(
            inventory_item=item,
            quantity=5,
            order_id=str(uuid.uuid4()),
        )
        
        assert reservation.quantity == 5
        item.refresh_from_db()
        assert item.reserved_qty == 15
    
    def test_confirm_reservation(self):
        """Test reservation confirmation."""
        item = InventoryItemFactory(available_qty=100, reserved_qty=10)
        reservation = InventoryReservationFactory(
            inventory_item=item,
            quantity=10,
            status='pending'
        )
        
        InventoryService.confirm_reservation(reservation)
        
        reservation.refresh_from_db()
        assert reservation.status == 'confirmed'
    
    def test_release_reservation(self):
        """Test reservation release restores stock."""
        item = InventoryItemFactory(available_qty=100, reserved_qty=10)
        reservation = InventoryReservationFactory(
            inventory_item=item,
            quantity=10,
            status='pending'
        )
        
        InventoryService.release_reservation(reservation)
        
        item.refresh_from_db()
        assert item.reserved_qty == 0
        
        reservation.refresh_from_db()
        assert reservation.status == 'released'


class TestInventoryServiceAdjustment:
    """Tests for stock adjustment operations."""
    
    def test_adjust_stock_increase(self):
        """Test increasing stock."""
        item = InventoryItemFactory(available_qty=100)
        user = UserFactory()
        
        movement = InventoryService.adjust_stock(
            inventory_item=item,
            quantity_delta=50,
            notes='Stock received',
            user=user,
        )
        
        assert movement.quantity == 50
        assert movement.movement_type == 'adjustment'
        
        item.refresh_from_db()
        assert item.available_qty == 150
    
    def test_adjust_stock_decrease(self):
        """Test decreasing stock."""
        item = InventoryItemFactory(available_qty=100, reserved_qty=0)
        
        movement = InventoryService.adjust_stock(
            inventory_item=item,
            quantity_delta=-30,
            notes='Damaged goods',
        )
        
        assert movement.quantity == -30
        
        item.refresh_from_db()
        assert item.available_qty == 70
    
    def test_adjust_stock_negative_result_raises(self):
        """Test adjustment that would result in negative stock."""
        item = InventoryItemFactory(available_qty=10)
        
        with pytest.raises(ValueError) as exc:
            InventoryService.adjust_stock(
                inventory_item=item,
                quantity_delta=-20,
                notes='Invalid adjustment',
            )
        
        assert 'negative stock' in str(exc.value).lower()
    
    def test_adjust_stock_below_reserved_raises(self):
        """Test adjustment that would go below reserved qty."""
        item = InventoryItemFactory(available_qty=100, reserved_qty=80)
        
        with pytest.raises(ValueError) as exc:
            InventoryService.adjust_stock(
                inventory_item=item,
                quantity_delta=-30,  # Would make available=70 < reserved=80
                notes='Invalid adjustment',
            )
        
        assert 'reserved' in str(exc.value).lower()


class TestInventoryServiceTransfer:
    """Tests for stock transfer operations."""
    
    def test_transfer_stock_success(self):
        """Test successful stock transfer."""
        company = CompanyFactory()
        from_location = LocationFactory(company=company, code='WH-1')
        to_location = LocationFactory(company=company, code='WH-2')
        
        from_item = InventoryItemFactory(
            company=company,
            location=from_location,
            available_qty=100,
            reserved_qty=0
        )
        to_item = InventoryItemFactory(
            company=company,
            product=from_item.product,
            location=to_location,
            available_qty=20,
            reserved_qty=0
        )
        
        out_movement, in_movement = InventoryService.transfer_stock(
            from_item=from_item,
            to_item=to_item,
            quantity=30,
            notes='Stock rebalancing',
        )
        
        assert out_movement.movement_type == 'transfer_out'
        assert out_movement.quantity == -30
        assert in_movement.movement_type == 'transfer_in'
        assert in_movement.quantity == 30
        
        from_item.refresh_from_db()
        to_item.refresh_from_db()
        
        assert from_item.available_qty == 70
        assert to_item.available_qty == 50
    
    def test_transfer_stock_insufficient(self):
        """Test transfer with insufficient source stock."""
        company = CompanyFactory()
        from_item = InventoryItemFactory(company=company, available_qty=10)
        to_item = InventoryItemFactory(
            company=company,
            product=from_item.product,
            available_qty=0
        )
        
        with pytest.raises(InsufficientStockError):
            InventoryService.transfer_stock(
                from_item=from_item,
                to_item=to_item,
                quantity=20,
            )


class TestInventoryServiceUtilities:
    """Tests for utility methods."""
    
    def test_check_low_stock(self):
        """Test low stock detection."""
        company = CompanyFactory()
        location = LocationFactory(company=company)
        
        # Low stock item
        InventoryItemFactory(
            company=company,
            location=location,
            available_qty=5,
            reorder_point=10
        )
        
        # Normal stock item
        InventoryItemFactory(
            company=company,
            location=location,
            available_qty=50,
            reorder_point=10
        )
        
        low_stock_items = InventoryService.check_low_stock(company=company)
        
        assert len(low_stock_items) == 1
        assert low_stock_items[0].net_qty < low_stock_items[0].reorder_point
    
    def test_get_stock_levels(self):
        """Test aggregated stock levels."""
        company = CompanyFactory()
        location1 = LocationFactory(company=company, code='WH-1')
        location2 = LocationFactory(company=company, code='WH-2')
        
        item1 = InventoryItemFactory(
            company=company,
            location=location1,
            available_qty=100,
            reserved_qty=10
        )
        InventoryItemFactory(
            company=company,
            product=item1.product,
            location=location2,
            available_qty=50,
            reserved_qty=5
        )
        
        levels = InventoryService.get_stock_levels(
            product=item1.product,
            company=company
        )
        
        assert levels['total_available'] == 150
        assert levels['total_reserved'] == 15
        assert levels['total_net'] == 135
        assert len(levels['by_location']) == 2
    
    def test_cleanup_expired_reservations(self):
        """Test expired reservation cleanup."""
        company = CompanyFactory()
        item = InventoryItemFactory(company=company, available_qty=100, reserved_qty=10)
        
        # Create expired reservation
        expired = InventoryReservationFactory(
            inventory_item=item,
            quantity=10,
            status='pending',
            expires_at=timezone.now() - timedelta(minutes=5)
        )
        
        # Create active reservation
        active = InventoryReservationFactory(
            inventory_item=item,
            quantity=5,
            status='pending',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        count = InventoryService.cleanup_expired_reservations(company=company)
        
        assert count == 1
        
        expired.refresh_from_db()
        assert expired.status == 'expired'
        
        active.refresh_from_db()
        assert active.status == 'pending'
