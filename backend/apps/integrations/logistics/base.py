"""
Abstract base class for logistics adapters.

Provides a common interface for integrating with shipping carriers.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, Dict, Any, List


@dataclass
class ShippingRate:
    """
    Shipping rate quote from a carrier.
    """
    provider: str
    service_type: str
    service_name: str
    price: Decimal
    currency: str = 'SGD'
    estimated_days: int = 3
    estimated_delivery: Optional[str] = None
    rate_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Shipment:
    """
    Created shipment with tracking info.
    """
    id: str
    tracking_number: str
    provider: str
    service_type: str
    status: str
    label_url: Optional[str] = None
    created_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrackingEvent:
    """
    Tracking event for a shipment.
    """
    timestamp: str
    status: str
    location: str
    description: str


class LogisticsAdapter(ABC):
    """
    Abstract base class for logistics carrier adapters.
    
    Implement this class to add support for a new carrier.
    Each adapter should handle:
    - Rate quotes
    - Shipment creation
    - Label generation
    - Tracking
    """
    
    name: str = 'base'
    display_name: str = 'Base Carrier'
    
    @abstractmethod
    def get_rates(
        self,
        origin_postal: str,
        destination_postal: str,
        weight_grams: int,
        dimensions: Optional[Dict[str, int]] = None,
    ) -> List[ShippingRate]:
        """
        Get shipping rate quotes.
        
        Args:
            origin_postal: Origin postal code
            destination_postal: Destination postal code
            weight_grams: Package weight in grams
            dimensions: Optional {length, width, height} in cm
            
        Returns:
            List of ShippingRate options
        """
        pass
    
    @abstractmethod
    def create_shipment(
        self,
        rate_id: str,
        sender: Dict[str, Any],
        recipient: Dict[str, Any],
        order_ref: str,
    ) -> Shipment:
        """
        Create a shipment and generate label.
        
        Args:
            rate_id: Selected rate ID
            sender: Sender address details
            recipient: Recipient address details
            order_ref: Order reference number
            
        Returns:
            Created Shipment with tracking number
        """
        pass
    
    @abstractmethod
    def get_tracking(
        self,
        tracking_number: str,
    ) -> List[TrackingEvent]:
        """
        Get tracking history for a shipment.
        
        Args:
            tracking_number: Carrier tracking number
            
        Returns:
            List of TrackingEvent in chronological order
        """
        pass
    
    def cancel_shipment(self, shipment_id: str) -> bool:
        """
        Cancel a shipment if possible.
        
        Args:
            shipment_id: Carrier shipment ID
            
        Returns:
            True if cancellation successful
        """
        raise NotImplementedError("Subclass may implement cancel_shipment")
    
    def schedule_pickup(
        self,
        shipment_ids: List[str],
        pickup_date: str,
        pickup_time: str,
    ) -> str:
        """
        Schedule pickup for shipments.
        
        Args:
            shipment_ids: List of shipment IDs
            pickup_date: Pickup date (YYYY-MM-DD)
            pickup_time: Pickup time slot
            
        Returns:
            Pickup confirmation reference
        """
        raise NotImplementedError("Subclass may implement schedule_pickup")
