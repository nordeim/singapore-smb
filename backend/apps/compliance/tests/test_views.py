"""
Compliance API view tests.
"""
import pytest
from decimal import Decimal
from uuid import uuid4

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.compliance.models import GSTReturn, DataAccessRequest
from apps.compliance.tests.factories import (
    GSTReturnFactory, ValidatedGSTReturnFactory,
    DataAccessRequestFactory,
)
from apps.accounts.tests.factories import CompanyFactory, UserFactory
from apps.commerce.tests.factories import CustomerFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client(api_client):
    """Create authenticated API client."""
    user = UserFactory()
    api_client.force_authenticate(user=user)
    api_client.user = user
    return api_client


@pytest.mark.django_db
class TestGSTReturnViewSet:
    """Tests for GST return API."""
    
    def test_list_returns(self, authenticated_client):
        """Test listing GST returns."""
        GSTReturnFactory(company=authenticated_client.user.company)
        
        response = authenticated_client.get('/api/v1/compliance/gst-returns/')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_return_detail(self, authenticated_client):
        """Test getting GST return details."""
        gst_return = GSTReturnFactory(company=authenticated_client.user.company)
        
        response = authenticated_client.get(
            f'/api/v1/compliance/gst-returns/{gst_return.id}/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['quarter'] == gst_return.quarter
    
    def test_validate_return_action(self, authenticated_client):
        """Test validate action."""
        gst_return = GSTReturnFactory(company=authenticated_client.user.company)
        
        response = authenticated_client.post(
            f'/api/v1/compliance/gst-returns/{gst_return.id}/validate/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'is_valid' in response.data
    
    def test_submit_return_action(self, authenticated_client):
        """Test submit action."""
        gst_return = ValidatedGSTReturnFactory(
            company=authenticated_client.user.company
        )
        
        response = authenticated_client.post(
            f'/api/v1/compliance/gst-returns/{gst_return.id}/submit/',
            {'iras_reference': 'TEST-123'}
        )
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestDataAccessRequestViewSet:
    """Tests for data access request API."""
    
    def test_list_requests(self, authenticated_client):
        """Test listing data access requests."""
        customer = CustomerFactory(company=authenticated_client.user.company)
        DataAccessRequestFactory(
            company=authenticated_client.user.company,
            customer=customer,
        )
        
        response = authenticated_client.get('/api/v1/compliance/data-requests/')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_create_request(self, authenticated_client):
        """Test creating a data access request."""
        customer = CustomerFactory(company=authenticated_client.user.company)
        
        response = authenticated_client.post(
            '/api/v1/compliance/data-requests/',
            {
                'customer_id': str(customer.id),
                'request_type': 'access',
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['request_type'] == 'access'
    
    def test_complete_request_action(self, authenticated_client):
        """Test complete action."""
        customer = CustomerFactory(company=authenticated_client.user.company)
        request = DataAccessRequestFactory(
            company=authenticated_client.user.company,
            customer=customer,
        )
        
        response = authenticated_client.post(
            f'/api/v1/compliance/data-requests/{request.id}/complete/',
            {'notes': 'Data exported'}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'completed'


@pytest.mark.django_db  
class TestAuditLogViewSet:
    """Tests for audit log API."""
    
    def test_list_audit_logs(self, authenticated_client):
        """Test listing audit logs."""
        from apps.compliance.tests.factories import AuditLogFactory
        
        AuditLogFactory(company=authenticated_client.user.company)
        
        response = authenticated_client.get('/api/v1/compliance/audit-logs/')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_audit_logs_read_only(self, authenticated_client):
        """Test that audit logs cannot be created via API."""
        response = authenticated_client.post(
            '/api/v1/compliance/audit-logs/',
            {'action': 'TEST'}
        )
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
