"""
SingPost logistics adapter.

Singapore Post national postal service.
"""
import logging
from decimal import Decimal
from typing import Optional, Dict, Any, List

from django.conf import settings

from apps.integrations.logistics.base import (
    LogisticsAdapter, ShippingRate, Shipment, TrackingEvent,
)


logger = logging.getLogger(__name__)


class SingPostAdapter(LogisticsAdapter):
    """
    SingPost delivery adapter.
    
    Features:
    - Registered mail
    - Speedpost
    - POPStation pickup
    """
    
    name = 'singpost'
    display_name = 'SingPost'
    
    # API endpoints
    API_URL = 'https://api.singpost.com'
    
    def __init__(self):
        self._httpx = None
    
    @property
    def api_key(self) -> str:
        return getattr(settings, 'SINGPOST_API_KEY', '')
    
    @property
    def httpx(self):
        if self._httpx is None:
            try:
                import httpx
                self._httpx = httpx
            except ImportError:
                raise ImportError("httpx package required for SingPost integration")
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
        """Get SingPost shipping rates."""
        
        # SingPost domestic rates (simplified)
        rates = []
        
        # Normal mail (up to 500g)
        if weight_grams <= 500:
            if weight_grams <= 100:
                mail_price = Decimal('0.90')
            elif weight_grams <= 250:
                mail_price = Decimal('1.30')
            else:
                mail_price = Decimal('1.60')
            
            rates.append(ShippingRate(
                provider=self.name,
                service_type='normal_mail',
                service_name='SingPost Normal Mail',
                price=mail_price,
                estimated_days=3,
                rate_id=f'sp_mail_{weight_grams}g',
            ))
        
        # Registered mail
        if weight_grams <= 2000:
            if weight_grams <= 100:
                reg_price = Decimal('2.80')
            elif weight_grams <= 250:
                reg_price = Decimal('3.20')
            elif weight_grams <= 500:
                reg_price = Decimal('3.60')
            else:
                reg_price = Decimal('4.50')
            
            rates.append(ShippingRate(
                provider=self.name,
                service_type='registered_mail',
                service_name='SingPost Registered Mail',
                price=reg_price,
                estimated_days=2,
                rate_id=f'sp_reg_{weight_grams}g',
            ))
        
        # Speedpost (for heavier items)
        if weight_grams <= 10000:
            if weight_grams <= 1000:
                speed_price = Decimal('5.00')
            elif weight_grams <= 3000:
                speed_price = Decimal('7.00')
            else:
                speed_price = Decimal('10.00')
            
            rates.append(ShippingRate(
                provider=self.name,
                service_type='speedpost',
                service_name='Speedpost Islandwide',
                price=speed_price,
                estimated_days=1,
                rate_id=f'sp_speed_{weight_grams}g',
            ))
        
        return rates
    
    def create_shipment(
        self,
        rate_id: str,
        sender: Dict[str, Any],
        recipient: Dict[str, Any],
        order_ref: str,
    ) -> Shipment:
        """Create a SingPost shipment."""
        try:
            # Determine service type from rate_id
            if 'speed' in rate_id:
                service = 'SPEEDPOST'
            elif 'reg' in rate_id:
                service = 'REGISTERED'
            else:
                service = 'NORMAL'
            
            payload = {
                'service_code': service,
                'order_reference': order_ref,
                'parcel': {
                    'weight': 1.0,
                    'length': 20,
                    'width': 15,
                    'height': 10,
                },
                'sender': {
                    'name': sender.get('name'),
                    'phone': sender.get('phone'),
                    'address1': sender.get('address_line1'),
                    'address2': sender.get('address_line2', ''),
                    'postcode': sender.get('postal_code'),
                    'country': 'SG',
                },
                'recipient': {
                    'name': recipient.get('name'),
                    'phone': recipient.get('phone'),
                    'address1': recipient.get('address_line1'),
                    'address2': recipient.get('address_line2', ''),
                    'postcode': recipient.get('postal_code'),
                    'country': 'SG',
                },
            }
            
            response = self.httpx.post(
                f'{self.API_URL}/shipments',
                headers=self._get_headers(),
                json=payload,
                timeout=30.0,
            )
            
            if response.status_code not in [200, 201]:
                logger.error(f"SingPost error: {response.text}")
                raise Exception(f"SingPost API error: {response.status_code}")
            
            result = response.json()
            
            return Shipment(
                id=result.get('shipment_id', ''),
                tracking_number=result.get('tracking_number', order_ref),
                provider=self.name,
                service_type=service,
                status='created',
                label_url=result.get('label_url'),
            )
            
        except Exception as e:
            logger.error(f"SingPost shipment error: {e}")
            raise
    
    def get_tracking(
        self,
        tracking_number: str,
    ) -> List[TrackingEvent]:
        """Get SingPost tracking history."""
        try:
            response = self.httpx.get(
                f'{self.API_URL}/tracking/{tracking_number}',
                headers=self._get_headers(),
                timeout=30.0,
            )
            
            if response.status_code != 200:
                return []
            
            result = response.json()
            events = []
            
            for event in result.get('events', []):
                events.append(TrackingEvent(
                    timestamp=event.get('date', ''),
                    status=event.get('status_code', ''),
                    location=event.get('location', 'Singapore'),
                    description=event.get('description', ''),
                ))
            
            return events
            
        except Exception as e:
            logger.error(f"SingPost tracking error: {e}")
            return []
