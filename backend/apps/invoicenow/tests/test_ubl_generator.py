"""
UBL Generator tests.
"""
import pytest
from decimal import Decimal
from unittest.mock import MagicMock

from apps.invoicenow.services.ubl_generator import UBLGenerator


class TestUBLGenerator:
    """Tests for UBL XML generation."""
    
    def test_generate_creates_xml(self):
        """Test that generate creates valid XML."""
        # Mock invoice
        invoice = MagicMock()
        invoice.invoice_number = 'INV-2024-001'
        invoice.invoice_date.isoformat.return_value = '2024-01-15'
        invoice.due_date.isoformat.return_value = '2024-02-14'
        invoice.subtotal = Decimal('100.00')
        invoice.tax_amount = Decimal('9.00')
        invoice.total_amount = Decimal('109.00')
        invoice.amount_due = Decimal('109.00')
        invoice.currency = 'SGD'
        
        # Mock company
        invoice.company.name = 'Test Company'
        invoice.company.uen = '202400001A'
        invoice.company.gst_registration_number = 'M2-0000001-0'
        invoice.company.address_line1 = '123 Test Street'
        invoice.company.city = 'Singapore'
        invoice.company.postal_code = '188216'
        
        # Mock customer
        invoice.customer.email = 'customer@example.com'
        invoice.customer.company_name = 'Customer Ltd'
        invoice.customer.company_uen = '202400002B'
        invoice.customer.first_name = 'John'
        invoice.customer.last_name = 'Doe'
        
        # Mock line
        line = MagicMock()
        line.description = 'Test Product'
        line.quantity = 1
        line.unit_price = Decimal('100.00')
        line.line_total = Decimal('100.00')
        line.gst_code = 'SR'
        line.tax_rate = 9
        line.unit_of_measure = 'EA'
        invoice.lines.all.return_value = [line]
        
        xml = UBLGenerator.generate(invoice)
        
        assert '<?xml version' in xml
        assert 'Invoice' in xml
        assert 'INV-2024-001' in xml
    
    def test_generate_includes_customization_id(self):
        """Test that output includes PEPPOL customization ID."""
        invoice = MagicMock()
        invoice.invoice_number = 'INV-001'
        invoice.invoice_date.isoformat.return_value = '2024-01-15'
        invoice.due_date = None
        invoice.subtotal = Decimal('100.00')
        invoice.tax_amount = Decimal('9.00')
        invoice.total_amount = Decimal('109.00')
        invoice.amount_due = Decimal('109.00')
        invoice.currency = 'SGD'
        
        invoice.company.name = 'Test'
        invoice.company.uen = '123'
        invoice.company.gst_registration_number = None
        invoice.company.address_line1 = None
        invoice.company.city = None
        invoice.company.postal_code = None
        
        invoice.customer.email = 'test@test.com'
        invoice.customer.company_name = 'Test'
        invoice.customer.company_uen = None
        invoice.customer.first_name = 'Test'
        invoice.customer.last_name = 'User'
        
        invoice.lines.all.return_value = []
        
        xml = UBLGenerator.generate(invoice)
        
        assert 'peppol' in xml.lower()
    
    def test_gst_category_mapping(self):
        """Test GST code to PEPPOL category mapping."""
        assert UBLGenerator._get_tax_category('SR') == 'S'
        assert UBLGenerator._get_tax_category('ZR') == 'Z'
        assert UBLGenerator._get_tax_category('ES') == 'E'
        assert UBLGenerator._get_tax_category('OS') == 'O'
