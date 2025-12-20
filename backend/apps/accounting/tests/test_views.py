"""
Tests for accounting views.
"""
import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounting.models import Account, JournalEntry, Invoice, Payment
from apps.accounting.tests.factories import (
    AccountFactory, AssetAccountFactory, RevenueAccountFactory,
    JournalEntryFactory,
    InvoiceFactory,
    PaymentFactory,
)
from apps.accounts.tests.factories import CompanyFactory, UserFactory


pytestmark = pytest.mark.django_db


class TestAccountViewSet:
    """Tests for AccountViewSet."""
    
    @pytest.fixture
    def api_client(self):
        """Create authenticated API client."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        client.user = user
        return client
    
    def test_list_accounts(self, api_client):
        """Test listing accounts."""
        # Create accounts for user's company
        AccountFactory(company=api_client.user.company)
        AccountFactory(company=api_client.user.company)
        
        # Create account for another company (should not appear)
        AccountFactory()
        
        response = api_client.get('/api/v1/accounting/accounts/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_create_account(self, api_client):
        """Test creating account."""
        data = {
            'code': '1500',
            'name': 'Prepaid Expenses',
            'account_type': 'asset',
            'account_subtype': 'current',
        }
        
        response = api_client.post('/api/v1/accounting/accounts/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['code'] == '1500'
        assert response.data['name'] == 'Prepaid Expenses'
    
    def test_tree_action(self, api_client):
        """Test tree endpoint for hierarchical view."""
        parent = AccountFactory(
            company=api_client.user.company,
            code='1000',
            parent=None
        )
        child = AccountFactory(
            company=api_client.user.company,
            code='1100',
            parent=parent
        )
        
        response = api_client.get('/api/v1/accounting/accounts/tree/')
        
        assert response.status_code == status.HTTP_200_OK
        # Root should have children
        roots = response.data
        assert len(roots) >= 1


class TestJournalEntryViewSet:
    """Tests for JournalEntryViewSet."""
    
    @pytest.fixture
    def api_client(self):
        """Create authenticated API client."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        client.user = user
        return client
    
    def test_list_journal_entries(self, api_client):
        """Test listing journal entries."""
        JournalEntryFactory(company=api_client.user.company)
        
        response = api_client.get('/api/v1/accounting/journals/')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_create_journal_entry(self, api_client):
        """Test creating journal entry via API."""
        debit_account = AssetAccountFactory(
            company=api_client.user.company, code='1100'
        )
        credit_account = RevenueAccountFactory(
            company=api_client.user.company, code='4000'
        )
        
        data = {
            'entry_date': date.today().isoformat(),
            'description': 'Test entry',
            'lines': [
                {
                    'account_id': str(debit_account.id),
                    'debit_amount': '100.00',
                    'credit_amount': '0.00',
                },
                {
                    'account_id': str(credit_account.id),
                    'debit_amount': '0.00',
                    'credit_amount': '100.00',
                },
            ],
        }
        
        response = api_client.post(
            '/api/v1/accounting/journals/',
            data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'draft'
        assert response.data['total_debit'] == '100.00'
    
    def test_post_action(self, api_client):
        """Test posting a journal entry."""
        # Create entry with lines for user's company
        company = api_client.user.company
        debit_account = AssetAccountFactory(company=company, code='1100')
        credit_account = RevenueAccountFactory(company=company, code='4000')
        
        entry = JournalEntryFactory(company=company)
        
        # Add balanced lines
        from apps.accounting.models import JournalLine
        JournalLine.objects.create(
            journal_entry=entry,
            account=debit_account,
            debit_amount=Decimal('100.00'),
            credit_amount=Decimal('0.00'),
        )
        JournalLine.objects.create(
            journal_entry=entry,
            account=credit_account,
            debit_amount=Decimal('0.00'),
            credit_amount=Decimal('100.00'),
        )
        
        # Update totals after adding all lines
        entry.update_totals()
        
        response = api_client.post(
            f'/api/v1/accounting/journals/{entry.id}/post/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'posted'



class TestInvoiceViewSet:
    """Tests for InvoiceViewSet."""
    
    @pytest.fixture
    def api_client(self):
        """Create authenticated API client."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        client.user = user
        return client
    
    def test_list_invoices(self, api_client):
        """Test listing invoices."""
        InvoiceFactory(company=api_client.user.company)
        
        response = api_client.get('/api/v1/accounting/invoices/')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_send_action(self, api_client):
        """Test send action marks invoice as sent."""
        invoice = InvoiceFactory(
            company=api_client.user.company,
            status='draft'
        )
        
        response = api_client.post(
            f'/api/v1/accounting/invoices/{invoice.id}/send/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'sent'
    
    def test_aging_action(self, api_client):
        """Test aging summary action."""
        response = api_client.get('/api/v1/accounting/invoices/aging/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'current' in response.data
        assert 'total' in response.data


class TestPaymentViewSet:
    """Tests for PaymentViewSet."""
    
    @pytest.fixture
    def api_client(self):
        """Create authenticated API client."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        client.user = user
        return client
    
    def test_list_payments(self, api_client):
        """Test listing payments."""
        PaymentFactory(company=api_client.user.company)
        
        response = api_client.get('/api/v1/accounting/payments/')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_complete_action(self, api_client):
        """Test complete action marks payment as completed."""
        payment = PaymentFactory(
            company=api_client.user.company,
            status='pending'
        )
        
        response = api_client.post(
            f'/api/v1/accounting/payments/{payment.id}/complete/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'completed'
    
    def test_refund_action(self, api_client):
        """Test refund action."""
        payment = PaymentFactory(
            company=api_client.user.company,
            status='completed',
            amount=Decimal('100.00')
        )
        
        response = api_client.post(
            f'/api/v1/accounting/payments/{payment.id}/refund/',
            {'amount': '50.00'},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK


class TestGSTF5ViewSet:
    """Tests for GST F5 ViewSet."""
    
    @pytest.fixture
    def api_client(self):
        """Create authenticated API client."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        client.user = user
        return client
    
    def test_prepare_f5(self, api_client):
        """Test F5 preparation endpoint."""
        data = {
            'quarter': 1,
            'year': 2024,
        }
        
        response = api_client.post(
            '/api/v1/accounting/gst/f5/prepare/',
            data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'box_1' in response.data
        assert 'box_8' in response.data
    
    def test_validate_f5(self, api_client):
        """Test F5 validation endpoint."""
        data = {
            'company_id': str(api_client.user.company.id),
            'year': 2024,
            'quarter': 1,
            'period_start': '2024-01-01',
            'period_end': '2024-03-31',
            'box_1': '10000.00',
            'box_2': '0.00',
            'box_3': '0.00',
            'box_4': '10000.00',
            'box_5': '5000.00',
            'box_6': '900.00',
            'box_7': '450.00',
            'box_8': '450.00',
        }
        
        response = api_client.post(
            '/api/v1/accounting/gst/f5/validate/',
            data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'is_valid' in response.data
