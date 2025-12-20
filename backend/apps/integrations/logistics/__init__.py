# Logistics integrations
from apps.integrations.logistics.base import LogisticsAdapter, ShippingRate, Shipment
from apps.integrations.logistics.ninjavan import NinjaVanAdapter
from apps.integrations.logistics.singpost import SingPostAdapter


__all__ = [
    'LogisticsAdapter',
    'ShippingRate',
    'Shipment',
    'NinjaVanAdapter',
    'SingPostAdapter',
]
