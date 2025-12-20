"""
PEPPOL Service tests.
"""
import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock
import uuid

from apps.invoicenow.models import PEPPOLInvoice
from apps.invoicenow.services import PEPPOLService, UBLGenerator


@pytest.mark.django_db
class TestPEPPOLServicePrepare:
    """Tests for PEPPOLService prepare_invoice."""
    
    @patch.object(UBLGenerator, 'generate')
    def test_prepare_invoice_creates_record(self, mock_generate):
        """Test preparing an invoice creates PEPPOL record."""
        mock_generate.return_value = '<xml>test</xml>'
        
        from apps.accounting.tests.factories import InvoiceFactory
        
        invoice = InvoiceFactory()
        
        peppol_invoice = PEPPOLService.prepare_invoice(invoice)
        
        assert peppol_invoice.id is not None
        assert peppol_invoice.status == 'draft'
        assert peppol_invoice.invoice == invoice
    
    @patch.object(UBLGenerator, 'generate')
    def test_prepare_invoice_sets_endpoints(self, mock_generate):
        """Test that endpoints are set from company/customer."""
        mock_generate.return_value = '<xml>test</xml>'
        
        from apps.accounting.tests.factories import InvoiceFactory
        
        invoice = InvoiceFactory()
        invoice.company.uen = 'TEST123'
        invoice.company.save()
        
        peppol_invoice = PEPPOLService.prepare_invoice(invoice)
        
        assert peppol_invoice.sender_endpoint == 'TEST123'


@pytest.mark.django_db
class TestPEPPOLServiceValidate:
    """Tests for PEPPOLService validate_invoice."""
    
    def test_validate_fails_without_customer(self):
        """Test validation fails without customer."""
        peppol_invoice = MagicMock()
        peppol_invoice.invoice.invoice_number = 'INV-001'
        peppol_invoice.invoice.invoice_date = '2024-01-15'
        peppol_invoice.invoice.customer = None
        peppol_invoice.invoice.company.uen = '123'
        peppol_invoice.invoice.lines.count.return_value = 1
        peppol_invoice.invoice.total_amount = Decimal('100')
        peppol_invoice.status = 'draft'
        peppol_invoice.validation_errors = []
        
        is_valid, errors = PEPPOLService.validate_invoice(peppol_invoice)
        
        assert is_valid is False
        assert any('Customer' in e for e in errors)


@pytest.mark.django_db
class TestPEPPOLServiceAcknowledgment:
    """Tests for acknowledgment processing."""
    
    @patch.object(UBLGenerator, 'generate')
    def test_process_acknowledgment_creates_record(self, mock_generate):
        """Test processing acknowledgment."""
        mock_generate.return_value = '<xml>test</xml>'
        
        from apps.accounting.tests.factories import InvoiceFactory
        
        invoice = InvoiceFactory()
        peppol_invoice = PEPPOLService.prepare_invoice(invoice)
        
        # Manually set submitted status
        peppol_invoice.status = 'submitted'
        peppol_invoice.save()
        
        ack = PEPPOLService.process_acknowledgment(
            peppol_id=peppol_invoice.peppol_id,
            ack_type='delivery',
            response_code='AP',
            description='Delivered',
        )
        
        assert ack.id is not None
        assert ack.acknowledgment_type == 'delivery'
