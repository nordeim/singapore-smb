"""
URL configuration for inventory API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.inventory.views import (
    LocationViewSet,
    InventoryItemViewSet,
    InventoryMovementViewSet,
    InventoryReservationViewSet,
)


app_name = 'inventory'

router = DefaultRouter()
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'items', InventoryItemViewSet, basename='inventory-item')
router.register(r'movements', InventoryMovementViewSet, basename='inventory-movement')
router.register(r'reservations', InventoryReservationViewSet, basename='inventory-reservation')

urlpatterns = [
    path('', include(router.urls)),
]
