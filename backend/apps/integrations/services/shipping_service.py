"""
Shipping service for multi-carrier operations.
"""
import logging
from typing import List, Dict, Any, Optional

from apps.integrations.logistics import (
    ShippingRate, Shipment, NinjaVanAdapter, SingPostAdapter,
)


logger = logging.getLogger(__name__)


class ShippingService:
    """
    Service for aggregating shipping across multiple carriers.
    
    Provides:
    - Rate comparison across carriers
    - Shipment creation
    - Unified tracking
    """
    
    CARRIERS = {
        'ninjavan': NinjaVanAdapter,
        'singpost': SingPostAdapter,
    }
    
    @staticmethod
    def get_rates(
        origin_postal: str,
        destination_postal: str,
        weight_grams: int,
        dimensions: Optional[Dict[str, int]] = None,
    ) -> List[ShippingRate]:
        """
        Get rates from all carriers.
        
        Returns combined list sorted by price.
        """
        all_rates = []
        
        for carrier_name, adapter_class in ShippingService.CARRIERS.items():
            try:
                adapter = adapter_class()
                rates = adapter.get_rates(
                    origin_postal=origin_postal,
                    destination_postal=destination_postal,
                    weight_grams=weight_grams,
                    dimensions=dimensions,
                )
                all_rates.extend(rates)
            except Exception as e:
                logger.warning(f"Failed to get rates from {carrier_name}: {e}")
        
        # Sort by price
        all_rates.sort(key=lambda r: r.price)
        
        return all_rates
    
    @staticmethod
    def get_rates_for_order(order) -> List[ShippingRate]:
        """Get shipping rates for an order."""
        # Get shipping address
        shipping_address = order.shipping_address or {}
        
        destination_postal = shipping_address.get('postal_code', '')
        if not destination_postal:
            return []
        
        # Estimate weight from items
        weight_grams = 500  # Default
        if hasattr(order, 'items'):
            for item in order.items.all():
                weight_grams += 200 * item.quantity
        
        # Use company address as origin
        origin_postal = order.company.postal_code or '188216'
        
        return ShippingService.get_rates(
            origin_postal=origin_postal,
            destination_postal=destination_postal,
            weight_grams=weight_grams,
        )
    
    @staticmethod
    def create_shipment(
        order,
        rate_id: str,
    ) -> Shipment:
        """
        Create a shipment for an order.
        
        Args:
            order: Order to fulfill
            rate_id: Selected rate ID
            
        Returns:
            Created Shipment
        """
        # Determine carrier from rate_id
        if rate_id.startswith('nv_'):
            adapter = NinjaVanAdapter()
        elif rate_id.startswith('sp_'):
            adapter = SingPostAdapter()
        else:
            raise ValueError(f"Unknown rate ID format: {rate_id}")
        
        # Build sender from company
        sender = {
            'name': order.company.name,
            'phone': order.company.phone or '',
            'address_line1': order.company.address_line1 or '',
            'address_line2': order.company.address_line2 or '',
            'postal_code': order.company.postal_code or '',
        }
        
        # Build recipient from order
        shipping = order.shipping_address or {}
        recipient = {
            'name': shipping.get('name', ''),
            'phone': shipping.get('phone', ''),
            'address_line1': shipping.get('address_line1', ''),
            'address_line2': shipping.get('address_line2', ''),
            'postal_code': shipping.get('postal_code', ''),
        }
        
        shipment = adapter.create_shipment(
            rate_id=rate_id,
            sender=sender,
            recipient=recipient,
            order_ref=order.order_number,
        )
        
        logger.info(
            f"Created shipment {shipment.tracking_number} "
            f"for order {order.order_number}"
        )
        
        return shipment
    
    @staticmethod
    def get_tracking(tracking_number: str, carrier: str = None) -> List[Dict]:
        """
        Get tracking for a shipment.
        
        If carrier is not specified, tries all carriers.
        """
        events = []
        
        carriers_to_try = [carrier] if carrier else ShippingService.CARRIERS.keys()
        
        for carrier_name in carriers_to_try:
            if carrier_name not in ShippingService.CARRIERS:
                continue
                
            try:
                adapter = ShippingService.CARRIERS[carrier_name]()
                carrier_events = adapter.get_tracking(tracking_number)
                
                if carrier_events:
                    events = [
                        {
                            'timestamp': e.timestamp,
                            'status': e.status,
                            'location': e.location,
                            'description': e.description,
                            'carrier': carrier_name,
                        }
                        for e in carrier_events
                    ]
                    break
            except Exception as e:
                logger.debug(f"Tracking not found on {carrier_name}: {e}")
        
        return events
