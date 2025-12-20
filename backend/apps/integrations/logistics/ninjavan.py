"""
NinjaVan logistics adapter.

Singapore's leading last-mile delivery provider.
"""
import logging
from decimal import Decimal
from typing import Optional, Dict, Any, List

from django.conf import settings

from apps.integrations.logistics.base import (
    LogisticsAdapter, ShippingRate, Shipment, TrackingEvent,
)


logger = logging.getLogger(__name__)


class NinjaVanAdapter(LogisticsAdapter):
    """
    NinjaVan delivery adapter.
    
    Features:
    - Same-day and next-day delivery in Singapore
    - Cash on delivery support
    - Real-time tracking
    """
    
    name = 'ninjavan'
    display_name = 'Ninja Van'
    
    # API endpoints
    SANDBOX_URL = 'https://api-sandbox.ninjavan.co/sg'
    PRODUCTION_URL = 'https://api.ninjavan.co/sg'
    
    def __init__(self):
        self._httpx = None
    
    @property
    def api_url(self) -> str:
        is_sandbox = getattr(settings, 'NINJAVAN_SANDBOX', True)
        return self.SANDBOX_URL if is_sandbox else self.PRODUCTION_URL
    
    @property
    def api_key(self) -> str:
        return getattr(settings, 'NINJAVAN_API_KEY', '')
    
    @property
    def httpx(self):
        if self._httpx is None:
            try:
                import httpx
                self._httpx = httpx
            except ImportError:
                raise ImportError("httpx package required for NinjaVan integration")
        return self._httpx
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
    
    def get_rates(
        self,
        origin_postal: str,
        destination_postal: str,
        weight_grams: int,
        dimensions: Optional[Dict[str, int]] = None,
    ) -> List[ShippingRate]:
        """Get NinjaVan shipping rates."""
        
        # Calculate volumetric weight if dimensions provided
        volumetric_weight = 0
        if dimensions:
            volumetric_weight = (
                dimensions.get('length', 1) *
                dimensions.get('width', 1) *
                dimensions.get('height', 1)
            ) / 5000  # DIM factor
        
        # Use higher of actual or volumetric
        chargeable_weight = max(weight_grams / 1000, volumetric_weight)
        
        # NinjaVan rate tiers (simplified)
        # Actual rates should come from API
        if chargeable_weight <= 1:
            base_price = Decimal('3.50')
        elif chargeable_weight <= 3:
            base_price = Decimal('4.50')
        elif chargeable_weight <= 5:
            base_price = Decimal('6.00')
        else:
            base_price = Decimal('6.00') + Decimal('1.00') * Decimal(str((chargeable_weight - 5)))
        
        rates = [
            ShippingRate(
                provider=self.name,
                service_type='standard',
                service_name='Ninja Van Standard',
                price=base_price,
                estimated_days=2,
                rate_id=f'nv_std_{origin_postal}_{destination_postal}',
            ),
            ShippingRate(
                provider=self.name,
                service_type='express',
                service_name='Ninja Van Express',
                price=base_price + Decimal('2.00'),
                estimated_days=1,
                rate_id=f'nv_exp_{origin_postal}_{destination_postal}',
            ),
        ]
        
        return rates
    
    def create_shipment(
        self,
        rate_id: str,
        sender: Dict[str, Any],
        recipient: Dict[str, Any],
        order_ref: str,
    ) -> Shipment:
        """Create a NinjaVan shipment."""
        try:
            service_type = 'Parcel'
            if 'exp' in rate_id:
                service_type = 'Parcel Express'
            
            payload = {
                'service_type': service_type,
                'service_level': 'Standard',
                'from': {
                    'name': sender.get('name'),
                    'phone_number': sender.get('phone'),
                    'address': {
                        'address1': sender.get('address_line1'),
                        'address2': sender.get('address_line2', ''),
                        'postcode': sender.get('postal_code'),
                        'country': 'SG',
                    },
                },
                'to': {
                    'name': recipient.get('name'),
                    'phone_number': recipient.get('phone'),
                    'address': {
                        'address1': recipient.get('address_line1'),
                        'address2': recipient.get('address_line2', ''),
                        'postcode': recipient.get('postal_code'),
                        'country': 'SG',
                    },
                },
                'parcel_job': {
                    'allow_doorstep_dropoff': True,
                    'dimensions': {
                        'weight': 1.0,
                    },
                    'is_pickup_required': True,
                    'pickup_service_type': 'Scheduled',
                    'pickup_service_level': 'Standard',
                },
                'requested_tracking_number': order_ref,
            }
            
            response = self.httpx.post(
                f'{self.api_url}/4.2/orders',
                headers=self._get_headers(),
                json=payload,
                timeout=30.0,
            )
            
            if response.status_code not in [200, 201]:
                logger.error(f"NinjaVan error: {response.text}")
                raise Exception(f"NinjaVan API error: {response.status_code}")
            
            result = response.json()
            
            return Shipment(
                id=result.get('id', ''),
                tracking_number=result.get('tracking_number', order_ref),
                provider=self.name,
                service_type=service_type,
                status='created',
                label_url=result.get('label_url'),
            )
            
        except Exception as e:
            logger.error(f"NinjaVan shipment error: {e}")
            raise
    
    def get_tracking(
        self,
        tracking_number: str,
    ) -> List[TrackingEvent]:
        """Get NinjaVan tracking history."""
        try:
            response = self.httpx.get(
                f'{self.api_url}/1.0/orders/tracking/{tracking_number}',
                headers=self._get_headers(),
                timeout=30.0,
            )
            
            if response.status_code != 200:
                return []
            
            result = response.json()
            events = []
            
            for event in result.get('events', []):
                events.append(TrackingEvent(
                    timestamp=event.get('timestamp', ''),
                    status=event.get('status', ''),
                    location=event.get('location', ''),
                    description=event.get('description', ''),
                ))
            
            return events
            
        except Exception as e:
            logger.error(f"NinjaVan tracking error: {e}")
            return []
