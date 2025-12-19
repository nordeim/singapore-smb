"""
Inventory service for stock operations.

Provides business logic for:
- Stock reservations with Redis locking
- Stock adjustments with audit trail
- Transfers between locations
- Low stock detection
"""
import logging
from decimal import Decimal
from typing import Optional, List, Tuple, Dict, Any
from datetime import timedelta

from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone

from apps.inventory.models import (
    Location, InventoryItem, InventoryReservation, InventoryMovement,
)
from apps.inventory.locks import InventoryLock, MultiItemLock, LockAcquisitionError


logger = logging.getLogger(__name__)


class InsufficientStockError(Exception):
    """Raised when there's not enough stock for an operation."""
    pass


class OptimisticLockError(Exception):
    """Raised when optimistic locking fails (concurrent modification)."""
    pass


class InventoryService:
    """
    Service class for inventory operations.
    
    All stock-modifying operations use Redis distributed locks
    to ensure thread safety in concurrent environments.
    """
    
    @staticmethod
    def reserve_stock(
        inventory_item: InventoryItem,
        quantity: int,
        order_id: str,
        expires_minutes: int = 30,
    ) -> InventoryReservation:
        """
        Reserve stock for an order.
        
        Creates a reservation and increments reserved_qty on the item.
        Uses Redis lock to prevent race conditions.
        
        Args:
            inventory_item: The InventoryItem to reserve from
            quantity: Amount to reserve
            order_id: UUID of the order
            expires_minutes: Minutes until reservation expires (default 30)
            
        Returns:
            Created InventoryReservation
            
        Raises:
            InsufficientStockError: If not enough stock available
            LockAcquisitionError: If lock cannot be acquired
        """
        with InventoryLock(inventory_item.id):
            # Refresh from DB to get latest quantities
            inventory_item.refresh_from_db()
            
            # Check availability
            if not inventory_item.can_reserve(quantity):
                raise InsufficientStockError(
                    f"Cannot reserve {quantity} units of {inventory_item.sku}. "
                    f"Available: {inventory_item.net_qty}"
                )
            
            with transaction.atomic():
                # Create reservation
                reservation = InventoryReservation.objects.create(
                    inventory_item=inventory_item,
                    order_id=order_id,
                    quantity=quantity,
                    status='pending',
                    expires_at=timezone.now() + timedelta(minutes=expires_minutes),
                )
                
                # Update reserved quantity with optimistic lock
                updated = InventoryItem.objects.filter(
                    pk=inventory_item.pk,
                    version=inventory_item.version
                ).update(
                    reserved_qty=F('reserved_qty') + quantity,
                    version=F('version') + 1,
                    last_movement_at=timezone.now(),
                )
                
                if updated == 0:
                    raise OptimisticLockError(
                        f"Concurrent modification detected for {inventory_item.sku}"
                    )
                
                # Create movement log
                InventoryMovement.create_movement(
                    inventory_item=inventory_item,
                    movement_type='sale',
                    quantity=-quantity,
                    reference_type='reservation',
                    reference_id=reservation.id,
                    notes=f"Reserved for order {order_id}",
                )
                
                logger.info(
                    f"Reserved {quantity}x {inventory_item.sku} for order {order_id}"
                )
                
                return reservation
    
    @staticmethod
    def confirm_reservation(reservation: InventoryReservation) -> None:
        """
        Confirm a pending reservation.
        
        Args:
            reservation: The reservation to confirm
            
        Raises:
            ValueError: If reservation is not pending
        """
        with InventoryLock(reservation.inventory_item_id):
            reservation.refresh_from_db()
            reservation.confirm()
            logger.info(f"Confirmed reservation {reservation.id}")
    
    @staticmethod
    def release_reservation(reservation: InventoryReservation) -> None:
        """
        Release a reservation and restore available stock.
        
        Args:
            reservation: The reservation to release
        """
        with InventoryLock(reservation.inventory_item_id):
            reservation.refresh_from_db()
            
            if reservation.status in ['released', 'expired']:
                return  # Already released
            
            with transaction.atomic():
                quantity = reservation.quantity
                item = reservation.inventory_item
                
                # Restore reserved quantity
                updated = InventoryItem.objects.filter(
                    pk=item.pk,
                    version=item.version
                ).update(
                    reserved_qty=F('reserved_qty') - quantity,
                    version=F('version') + 1,
                    last_movement_at=timezone.now(),
                )
                
                if updated == 0:
                    # Refresh and retry without optimistic lock
                    item.refresh_from_db()
                    item.reserved_qty = max(0, item.reserved_qty - quantity)
                    item.increment_version()
                    item.update_movement_timestamp()
                    item.save()
                
                reservation.release()
                
                # Create movement log for return
                InventoryMovement.create_movement(
                    inventory_item=item,
                    movement_type='return',
                    quantity=quantity,
                    reference_type='reservation_release',
                    reference_id=reservation.id,
                    notes="Reservation released",
                )
                
                logger.info(
                    f"Released reservation {reservation.id}, "
                    f"restored {quantity}x {item.sku}"
                )
    
    @staticmethod
    def adjust_stock(
        inventory_item: InventoryItem,
        quantity_delta: int,
        notes: str = '',
        user=None,
    ) -> InventoryMovement:
        """
        Adjust stock level manually.
        
        Args:
            inventory_item: The InventoryItem to adjust
            quantity_delta: Amount to add (positive) or remove (negative)
            notes: Reason for adjustment
            user: User making the adjustment
            
        Returns:
            Created InventoryMovement
            
        Raises:
            ValueError: If adjustment would result in negative stock
        """
        with InventoryLock(inventory_item.id):
            inventory_item.refresh_from_db()
            
            new_qty = inventory_item.available_qty + quantity_delta
            if new_qty < 0:
                raise ValueError(
                    f"Adjustment would result in negative stock: "
                    f"{inventory_item.available_qty} + {quantity_delta} = {new_qty}"
                )
            
            # Check constraint: reserved cannot exceed available
            if new_qty < inventory_item.reserved_qty:
                raise ValueError(
                    f"Cannot reduce stock below reserved amount: "
                    f"available={new_qty}, reserved={inventory_item.reserved_qty}"
                )
            
            with transaction.atomic():
                # Create movement first (before update)
                movement = InventoryMovement.create_movement(
                    inventory_item=inventory_item,
                    movement_type='adjustment',
                    quantity=quantity_delta,
                    notes=notes,
                    user=user,
                )
                
                # Update stock
                inventory_item.available_qty = new_qty
                inventory_item.increment_version()
                inventory_item.update_movement_timestamp()
                inventory_item.save(update_fields=[
                    'available_qty', 'version', 'last_movement_at', 'updated_at'
                ])
                
                logger.info(
                    f"Adjusted {inventory_item.sku} by {quantity_delta:+d} "
                    f"(now {new_qty})"
                )
                
                return movement
    
    @staticmethod
    def transfer_stock(
        from_item: InventoryItem,
        to_item: InventoryItem,
        quantity: int,
        notes: str = '',
        user=None,
    ) -> Tuple[InventoryMovement, InventoryMovement]:
        """
        Transfer stock between locations.
        
        Atomically decrements source and increments destination.
        
        Args:
            from_item: Source inventory item
            to_item: Destination inventory item
            quantity: Amount to transfer
            notes: Transfer notes
            user: User performing transfer
            
        Returns:
            Tuple of (outbound movement, inbound movement)
            
        Raises:
            InsufficientStockError: If source doesn't have enough stock
        """
        # Use MultiItemLock to prevent deadlocks
        with MultiItemLock([from_item.id, to_item.id]):
            from_item.refresh_from_db()
            to_item.refresh_from_db()
            
            # Check source has enough stock
            if from_item.net_qty < quantity:
                raise InsufficientStockError(
                    f"Cannot transfer {quantity} from {from_item.location.code}. "
                    f"Available: {from_item.net_qty}"
                )
            
            with transaction.atomic():
                # Create outbound movement
                out_movement = InventoryMovement.create_movement(
                    inventory_item=from_item,
                    movement_type='transfer_out',
                    quantity=-quantity,
                    reference_type='transfer',
                    reference_id=to_item.id,
                    notes=notes,
                    user=user,
                )
                
                # Create inbound movement
                in_movement = InventoryMovement.create_movement(
                    inventory_item=to_item,
                    movement_type='transfer_in',
                    quantity=quantity,
                    reference_type='transfer',
                    reference_id=from_item.id,
                    notes=notes,
                    user=user,
                )
                
                # Update source
                from_item.available_qty -= quantity
                from_item.increment_version()
                from_item.update_movement_timestamp()
                from_item.save(update_fields=[
                    'available_qty', 'version', 'last_movement_at', 'updated_at'
                ])
                
                # Update destination
                to_item.available_qty += quantity
                to_item.increment_version()
                to_item.update_movement_timestamp()
                to_item.save(update_fields=[
                    'available_qty', 'version', 'last_movement_at', 'updated_at'
                ])
                
                logger.info(
                    f"Transferred {quantity}x from {from_item.location.code} "
                    f"to {to_item.location.code}"
                )
                
                return out_movement, in_movement
    
    @staticmethod
    def receive_stock(
        inventory_item: InventoryItem,
        quantity: int,
        unit_cost: Optional[Decimal] = None,
        notes: str = '',
        reference_id=None,
        user=None,
    ) -> InventoryMovement:
        """
        Receive stock from a purchase.
        
        Args:
            inventory_item: The InventoryItem to receive into
            quantity: Amount received
            unit_cost: Cost per unit for this receipt
            notes: Receipt notes
            reference_id: Optional purchase order reference
            user: User receiving the stock
            
        Returns:
            Created InventoryMovement
        """
        with InventoryLock(inventory_item.id):
            inventory_item.refresh_from_db()
            
            with transaction.atomic():
                # Create movement
                movement = InventoryMovement.create_movement(
                    inventory_item=inventory_item,
                    movement_type='purchase',
                    quantity=quantity,
                    reference_type='purchase_order' if reference_id else '',
                    reference_id=reference_id,
                    notes=notes,
                    user=user,
                )
                
                # Update stock
                inventory_item.available_qty += quantity
                if unit_cost:
                    inventory_item.unit_cost = unit_cost
                inventory_item.increment_version()
                inventory_item.update_movement_timestamp()
                inventory_item.save()
                
                logger.info(
                    f"Received {quantity}x {inventory_item.sku}"
                )
                
                return movement
    
    @staticmethod
    def check_low_stock(company) -> List[InventoryItem]:
        """
        Get all items below their reorder point.
        
        Args:
            company: Company to check
            
        Returns:
            List of InventoryItems with low stock
        """
        # Get items where net_qty < reorder_point
        # Since net_qty is computed, we filter in Python
        items = InventoryItem.objects.filter(
            company=company,
            location__is_active=True,
        ).select_related('product', 'location')
        
        low_stock_items = [
            item for item in items
            if item.is_low_stock
        ]
        
        return low_stock_items
    
    @staticmethod
    def get_stock_levels(
        product,
        company=None,
    ) -> Dict[str, Any]:
        """
        Get aggregated stock levels for a product across locations.
        
        Args:
            product: Product to check
            company: Optional company filter
            
        Returns:
            Dict with total_available, total_reserved, by_location
        """
        queryset = InventoryItem.objects.filter(product=product)
        if company:
            queryset = queryset.filter(company=company)
        
        items = queryset.select_related('location')
        
        total_available = sum(item.available_qty for item in items)
        total_reserved = sum(item.reserved_qty for item in items)
        
        by_location = [
            {
                'location_id': str(item.location.id),
                'location_code': item.location.code,
                'location_name': item.location.name,
                'available_qty': item.available_qty,
                'reserved_qty': item.reserved_qty,
                'net_qty': item.net_qty,
            }
            for item in items
        ]
        
        return {
            'product_id': str(product.id),
            'product_sku': product.sku,
            'total_available': total_available,
            'total_reserved': total_reserved,
            'total_net': total_available - total_reserved,
            'by_location': by_location,
        }
    
    @staticmethod
    def cleanup_expired_reservations(company=None) -> int:
        """
        Expire and release pending reservations past their expiry.
        
        Args:
            company: Optional company filter
            
        Returns:
            Count of expired reservations
        """
        now = timezone.now()
        
        queryset = InventoryReservation.objects.filter(
            status='pending',
            expires_at__lt=now,
        )
        
        if company:
            queryset = queryset.filter(inventory_item__company=company)
        
        count = 0
        for reservation in queryset.select_related('inventory_item'):
            try:
                reservation.expire()
                InventoryService.release_reservation(reservation)
                count += 1
            except Exception as e:
                logger.error(f"Error expiring reservation {reservation.id}: {e}")
        
        if count > 0:
            logger.info(f"Expired {count} reservations")
        
        return count
