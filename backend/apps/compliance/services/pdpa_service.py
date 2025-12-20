"""
PDPA compliance service.

Provides:
- Consent recording and management
- Customer data export
- Customer data anonymization
- Access request processing
"""
import logging
from typing import Optional
from datetime import datetime

from django.db import transaction
from django.utils import timezone

from apps.compliance.models import DataConsent, DataAccessRequest


logger = logging.getLogger(__name__)


class PDPAService:
    """
    Service for PDPA (Personal Data Protection Act) compliance operations.
    
    Singapore PDPA requires:
    - Explicit consent for data collection/processing
    - Right to access personal data
    - Right to correct personal data
    - Right to withdraw consent
    - Data access requests fulfilled within 30 days
    """
    
    @staticmethod
    def record_consent(
        customer,
        consent_type: str,
        is_granted: bool,
        source: str = '',
        ip_address: str = None,
        user_agent: str = '',
    ) -> DataConsent:
        """
        Record a consent decision and update customer fields.
        
        Args:
            customer: Customer giving/withdrawing consent
            consent_type: Type of consent (marketing, analytics, etc.)
            is_granted: True if consent given, False if withdrawn
            source: Where consent was recorded (registration, checkout, settings)
            ip_address: Request IP address
            user_agent: Browser user agent
            
        Returns:
            Created DataConsent record
        """
        consent = DataConsent.objects.record_consent(
            customer=customer,
            consent_type=consent_type,
            is_granted=is_granted,
            source=source,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        action = "granted" if is_granted else "withdrew"
        logger.info(
            f"Customer {customer.id} {action} {consent_type} consent"
        )
        
        return consent
    
    @staticmethod
    def get_consent_summary(customer) -> dict:
        """
        Get current consent state for a customer.
        
        Args:
            customer: Customer to check
            
        Returns:
            Dict with consent type -> bool mapping and timestamps
        """
        # Get current state from Customer model fields
        summary = {
            'marketing': {
                'granted': customer.consent_marketing,
                'timestamp': customer.consent_marketing_at,
            },
            'analytics': {
                'granted': customer.consent_analytics,
                'timestamp': customer.consent_analytics_at,
            },
        }
        
        # Get latest consent record for each type
        consent_types = ['order_processing', 'third_party', 'profiling', 'legal_compliance']
        for consent_type in consent_types:
            latest = DataConsent.objects.filter(
                customer=customer,
                consent_type=consent_type,
            ).order_by('-consent_timestamp').first()
            
            summary[consent_type] = {
                'granted': latest.is_granted if latest else False,
                'timestamp': latest.consent_timestamp if latest else None,
            }
        
        return summary
    
    @staticmethod
    def export_customer_data(customer) -> dict:
        """
        Export all personal data for a customer.
        
        This satisfies PDPA data access requests.
        
        Args:
            customer: Customer to export
            
        Returns:
            Dict containing all PII in structured format
        """
        # Basic customer info
        export = {
            'customer': {
                'id': str(customer.id),
                'email': customer.email,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'phone': customer.phone,
                'customer_type': customer.customer_type,
                'company_name': customer.company_name,
                'company_uen': customer.company_uen,
                'created_at': customer.created_at.isoformat() if customer.created_at else None,
            },
            'consent': PDPAService.get_consent_summary(customer),
            'addresses': [],
            'orders': [],
        }
        
        # Add addresses
        for address in customer.addresses.all():
            export['addresses'].append({
                'type': address.address_type,
                'name': address.recipient_name,
                'line1': address.address_line1,
                'line2': address.address_line2,
                'city': address.city,
                'postal_code': address.postal_code,
                'phone': address.phone,
            })
        
        # Add orders (summary only)
        for order in customer.orders.all():
            export['orders'].append({
                'order_number': order.order_number,
                'date': order.order_date.isoformat() if order.order_date else None,
                'status': order.status,
                'total': str(order.total_amount),
            })
        
        logger.info(f"Exported data for customer {customer.id}")
        
        return export
    
    @staticmethod
    def anonymize_customer(customer) -> None:
        """
        Anonymize customer personal data.
        
        This is used for PDPA deletion requests.
        Replaces PII with anonymized tokens while preserving
        order history for business records.
        
        Args:
            customer: Customer to anonymize
        """
        import hashlib
        
        # Generate anonymization token
        token = hashlib.sha256(str(customer.id).encode()).hexdigest()[:8]
        
        with transaction.atomic():
            # Anonymize customer fields
            customer.email = f"deleted_{token}@anonymized.local"
            customer.first_name = "Deleted"
            customer.last_name = f"Customer_{token}"
            customer.phone = ""
            customer.company_name = ""
            customer.company_uen = ""
            customer.notes = ""
            
            # Mark consents as withdrawn
            customer.consent_marketing = False
            customer.consent_analytics = False
            
            # Set data retention date
            customer.data_retention_until = timezone.now().date()
            
            customer.save()
            
            # Anonymize addresses
            for address in customer.addresses.all():
                address.recipient_name = f"Deleted_{token}"
                address.phone = ""
                address.address_line1 = "Anonymized"
                address.address_line2 = ""
                address.save()
        
        logger.info(f"Anonymized customer {customer.id}")
    
    @staticmethod
    def create_access_request(
        company,
        customer,
        request_type: str,
    ) -> DataAccessRequest:
        """
        Create a PDPA data access request.
        
        Args:
            company: Company receiving the request
            customer: Customer making the request
            request_type: access, correction, or deletion
            
        Returns:
            Created DataAccessRequest
        """
        request = DataAccessRequest.objects.create(
            company=company,
            customer=customer,
            request_type=request_type,
        )
        
        logger.info(
            f"Created {request_type} request {request.id} for customer {customer.id}"
        )
        
        return request
    
    @staticmethod
    def process_access_request(
        request: DataAccessRequest,
        action: str,
        notes: str,
        user=None,
    ) -> DataAccessRequest:
        """
        Process a data access request.
        
        Args:
            request: DataAccessRequest to process
            action: 'complete' or 'reject'
            notes: Response notes
            user: User processing the request
            
        Returns:
            Updated DataAccessRequest
        """
        if action == 'complete':
            request.complete(notes=notes, user=user)
            logger.info(f"Completed data request {request.id}")
        elif action == 'reject':
            request.reject(reason=notes, user=user)
            logger.info(f"Rejected data request {request.id}")
        else:
            raise ValueError(f"Invalid action: {action}")
        
        return request
    
    @staticmethod
    def get_pending_requests(company, include_overdue: bool = True) -> list:
        """
        Get pending data access requests for a company.
        
        Args:
            company: Company to check
            include_overdue: Include overdue indicator
            
        Returns:
            List of pending requests with SLA info
        """
        requests = DataAccessRequest.objects.filter(
            company=company,
            status__in=['pending', 'processing'],
        ).order_by('due_date')
        
        result = []
        for request in requests:
            result.append({
                'id': str(request.id),
                'customer': request.customer.email,
                'request_type': request.request_type,
                'status': request.status,
                'due_date': request.due_date.isoformat(),
                'days_until_due': request.days_until_due,
                'sla_status': request.sla_status,
            })
        
        return result
