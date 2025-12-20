"""
Logistics adapter tests.
"""
import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock

from apps.integrations.logistics.base import ShippingRate, Shipment, TrackingEvent
from apps.integrations.logistics.ninjavan import NinjaVanAdapter
from apps.integrations.logistics.singpost import SingPostAdapter
from apps.integrations.services import ShippingService


class TestShippingDataclasses:
    """Tests for shipping dataclasses."""
    
    def test_shipping_rate(self):
        """Test creating a shipping rate."""
        rate = ShippingRate(
            provider='ninjavan',
            service_type='standard',
            service_name='Ninja Van Standard',
            price=Decimal('4.50'),
        )
        
        assert rate.provider == 'ninjavan'
        assert rate.price == Decimal('4.50')
    
    def test_shipment(self):
        """Test creating a shipment."""
        shipment = Shipment(
            id='ship123',
            tracking_number='NV123456',
            provider='ninjavan',
            service_type='standard',
            status='created',
        )
        
        assert shipment.tracking_number == 'NV123456'


class TestNinjaVanAdapter:
    """Tests for NinjaVan adapter."""
    
    def test_get_rates(self):
        """Test getting NinjaVan rates."""
        adapter = NinjaVanAdapter()
        
        rates = adapter.get_rates(
            origin_postal='188216',
            destination_postal='238839',
            weight_grams=500,
        )
        
        assert len(rates) == 2  # Standard and Express
        assert all(r.provider == 'ninjavan' for r in rates)
    
    def test_express_rate_more_expensive(self):
        """Test that express is more expensive than standard."""
        adapter = NinjaVanAdapter()
        
        rates = adapter.get_rates(
            origin_postal='188216',
            destination_postal='238839',
            weight_grams=500,
        )
        
        standard = next(r for r in rates if r.service_type == 'standard')
        express = next(r for r in rates if r.service_type == 'express')
        
        assert express.price > standard.price


class TestSingPostAdapter:
    """Tests for SingPost adapter."""
    
    def test_get_rates_light_package(self):
        """Test getting rates for light package."""
        adapter = SingPostAdapter()
        
        rates = adapter.get_rates(
            origin_postal='188216',
            destination_postal='238839',
            weight_grams=100,
        )
        
        assert len(rates) >= 2  # Normal mail and registered
    
    def test_get_rates_heavy_package(self):
        """Test getting rates for heavy package."""
        adapter = SingPostAdapter()
        
        rates = adapter.get_rates(
            origin_postal='188216',
            destination_postal='238839',
            weight_grams=3000,
        )
        
        # Heavy packages only get registered and speedpost
        service_types = [r.service_type for r in rates]
        assert 'speedpost' in service_types


class TestShippingService:
    """Tests for ShippingService."""
    
    def test_get_rates_from_all_carriers(self):
        """Test getting rates from all carriers."""
        rates = ShippingService.get_rates(
            origin_postal='188216',
            destination_postal='238839',
            weight_grams=500,
        )
        
        # Should have rates from both carriers
        providers = set(r.provider for r in rates)
        assert 'ninjavan' in providers
        assert 'singpost' in providers
    
    def test_rates_sorted_by_price(self):
        """Test that rates are sorted by price."""
        rates = ShippingService.get_rates(
            origin_postal='188216',
            destination_postal='238839',
            weight_grams=500,
        )
        
        prices = [r.price for r in rates]
        assert prices == sorted(prices)
