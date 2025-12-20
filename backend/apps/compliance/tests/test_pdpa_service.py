"""
PDPA Service tests.
"""
import pytest
from decimal import Decimal
from datetime import date

from django.utils import timezone

from apps.compliance.models import DataConsent, DataAccessRequest
from apps.compliance.services import PDPAService
from apps.commerce.tests.factories import CustomerFactory
from apps.accounts.tests.factories import CompanyFactory, UserFactory


@pytest.mark.django_db
class TestPDPAServiceConsent:
    """Tests for PDPAService consent operations."""
    
    def test_record_consent_granted(self):
        """Test recording consent granted."""
        customer = CustomerFactory()
        
        consent = PDPAService.record_consent(
            customer=customer,
            consent_type='marketing',
            is_granted=True,
            source='registration',
            ip_address='192.168.1.1',
        )
        
        assert consent.is_granted is True
        assert consent.consent_type == 'marketing'
        assert consent.source == 'registration'
        
        # Check customer was updated
        customer.refresh_from_db()
        assert customer.consent_marketing is True
    
    def test_record_consent_withdrawn(self):
        """Test recording consent withdrawal."""
        customer = CustomerFactory(consent_marketing=True)
        
        consent = PDPAService.record_consent(
            customer=customer,
            consent_type='marketing',
            is_granted=False,
            source='settings',
        )
        
        assert consent.is_granted is False
        
        customer.refresh_from_db()
        assert customer.consent_marketing is False
    
    def test_get_consent_summary(self):
        """Test getting consent summary."""
        customer = CustomerFactory(
            consent_marketing=True,
            consent_analytics=False,
        )
        
        summary = PDPAService.get_consent_summary(customer)
        
        assert summary['marketing']['granted'] is True
        assert summary['analytics']['granted'] is False
    
    def test_consent_creates_audit_record(self):
        """Test that consent changes create audit records."""
        customer = CustomerFactory()
        initial_count = DataConsent.objects.filter(customer=customer).count()
        
        PDPAService.record_consent(
            customer=customer,
            consent_type='marketing',
            is_granted=True,
            source='test',
        )
        
        new_count = DataConsent.objects.filter(customer=customer).count()
        assert new_count == initial_count + 1


@pytest.mark.django_db
class TestPDPAServiceDataExport:
    """Tests for PDPAService data export."""
    
    def test_export_customer_data(self):
        """Test exporting customer data."""
        customer = CustomerFactory(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
        )
        
        export = PDPAService.export_customer_data(customer)
        
        assert export['customer']['email'] == 'john@example.com'
        assert export['customer']['first_name'] == 'John'
        assert 'consent' in export
        assert 'addresses' in export
        assert 'orders' in export
    
    def test_export_includes_addresses(self):
        """Test that export includes addresses."""
        from apps.commerce.tests.factories import CustomerAddressFactory
        
        customer = CustomerFactory()
        CustomerAddressFactory(customer=customer)
        
        export = PDPAService.export_customer_data(customer)
        
        assert len(export['addresses']) >= 1


@pytest.mark.django_db
class TestPDPAServiceAnonymization:
    """Tests for PDPAService anonymization."""
    
    def test_anonymize_customer(self):
        """Test anonymizing a customer."""
        customer = CustomerFactory(
            email='real@email.com',
            first_name='Real',
            last_name='Person',
            phone='+6512345678',
        )
        
        PDPAService.anonymize_customer(customer)
        
        customer.refresh_from_db()
        assert '@anonymized.local' in customer.email
        assert customer.first_name == 'Deleted'
        assert customer.phone == ''
        assert customer.consent_marketing is False


@pytest.mark.django_db
class TestPDPAServiceAccessRequests:
    """Tests for PDPAService access request operations."""
    
    def test_create_access_request(self):
        """Test creating a data access request."""
        company = CompanyFactory()
        customer = CustomerFactory(company=company)
        
        request = PDPAService.create_access_request(
            company=company,
            customer=customer,
            request_type='access',
        )
        
        assert request.id is not None
        assert request.request_type == 'access'
        assert request.status == 'pending'
    
    def test_process_access_request_complete(self):
        """Test completing a data access request."""
        company = CompanyFactory()
        customer = CustomerFactory(company=company)
        user = UserFactory()
        
        request = DataAccessRequest.objects.create(
            company=company,
            customer=customer,
            request_type='access',
        )
        
        result = PDPAService.process_access_request(
            request=request,
            action='complete',
            notes='Data exported and sent',
            user=user,
        )
        
        assert result.status == 'completed'
        assert result.response_notes == 'Data exported and sent'
    
    def test_process_access_request_reject(self):
        """Test rejecting a data access request."""
        company = CompanyFactory()
        customer = CustomerFactory(company=company)
        
        request = DataAccessRequest.objects.create(
            company=company,
            customer=customer,
            request_type='deletion',
        )
        
        result = PDPAService.process_access_request(
            request=request,
            action='reject',
            notes='Legal hold on data',
        )
        
        assert result.status == 'rejected'
    
    def test_get_pending_requests(self):
        """Test getting pending requests."""
        company = CompanyFactory()
        customer = CustomerFactory(company=company)
        
        # Create some requests
        DataAccessRequest.objects.create(
            company=company,
            customer=customer,
            request_type='access',
        )
        
        pending = PDPAService.get_pending_requests(company)
        
        assert len(pending) >= 1
        assert pending[0]['status'] == 'pending'
