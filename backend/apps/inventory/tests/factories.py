"""
Factory Boy factories for inventory models.
"""
import uuid
from decimal import Decimal

import factory
from factory.django import DjangoModelFactory

from apps.inventory.models import (
    Location, InventoryItem, InventoryReservation, InventoryMovement,
)
from apps.accounts.tests.factories import CompanyFactory, UserFactory
from apps.commerce.tests.factories import ProductFactory, ProductVariantFactory


class LocationFactory(DjangoModelFactory):
    """Factory for Location model."""
    
    class Meta:
        model = Location
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    code = factory.Sequence(lambda n: f"WH-{n:03d}")
    name = factory.Sequence(lambda n: f"Warehouse {n}")
    location_type = 'warehouse'
    address_line1 = factory.Faker('street_address')
    postal_code = factory.LazyFunction(
        lambda: str(factory.Faker._get_faker().random_int(100000, 999999))
    )
    is_active = True
    is_default = False
    settings = factory.LazyFunction(dict)


class StoreLocationFactory(LocationFactory):
    """Factory for store-type locations."""
    
    code = factory.Sequence(lambda n: f"STORE-{n:03d}")
    name = factory.Sequence(lambda n: f"Store {n}")
    location_type = 'store'


class InventoryItemFactory(DjangoModelFactory):
    """Factory for InventoryItem model."""
    
    class Meta:
        model = InventoryItem
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    product = factory.SubFactory(ProductFactory, company=factory.SelfAttribute('..company'))
    variant = None
    location = factory.SubFactory(LocationFactory, company=factory.SelfAttribute('..company'))
    available_qty = 100
    reserved_qty = 0
    reorder_point = 10
    reorder_quantity = 50
    unit_cost = Decimal('10.00')
    version = 1


class LowStockInventoryItemFactory(InventoryItemFactory):
    """Factory for low stock inventory items."""
    
    available_qty = 5
    reorder_point = 10


class InventoryReservationFactory(DjangoModelFactory):
    """Factory for InventoryReservation model."""
    
    class Meta:
        model = InventoryReservation
    
    id = factory.LazyFunction(uuid.uuid4)
    inventory_item = factory.SubFactory(InventoryItemFactory)
    order_id = factory.LazyFunction(uuid.uuid4)
    quantity = 5
    status = 'pending'


class InventoryMovementFactory(DjangoModelFactory):
    """Factory for InventoryMovement model."""
    
    class Meta:
        model = InventoryMovement
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    inventory_item = factory.SubFactory(InventoryItemFactory, company=factory.SelfAttribute('..company'))
    movement_type = 'adjustment'
    quantity = 10
    quantity_before = 100
    quantity_after = 110
    notes = 'Test movement'
    created_by = None
