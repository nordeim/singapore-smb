"""Integrations URL routing."""
from django.urls import path

from apps.integrations.views import (
    ShippingRatesView,
    CreateShipmentView,
    TrackingView,
)


urlpatterns = [
    path('shipping/rates/<uuid:order_id>/', ShippingRatesView.as_view(), name='shipping-rates'),
    path('shipping/create/', CreateShipmentView.as_view(), name='create-shipment'),
    path('shipping/tracking/<str:tracking_number>/', TrackingView.as_view(), name='tracking'),
]
