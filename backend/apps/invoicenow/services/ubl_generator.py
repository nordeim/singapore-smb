"""
UBL 2.1 Invoice Generator for PEPPOL BIS Billing 3.0.

Generates PEPPOL-compliant UBL XML invoices.
"""
import logging
from datetime import date
from decimal import Decimal
from typing import Optional
import xml.etree.ElementTree as ET

from django.conf import settings


logger = logging.getLogger(__name__)


# UBL 2.1 and PEPPOL namespaces
NAMESPACES = {
    'ubl': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
}


class UBLGenerator:
    """
    UBL 2.1 Invoice generator for PEPPOL BIS Billing 3.0.
    
    Generates XML invoices conforming to:
    - PEPPOL BIS Billing 3.0
    - Singapore InvoiceNow requirements
    """
    
    # PEPPOL profile and customization IDs
    CUSTOMIZATION_ID = 'urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0'
    PROFILE_ID = 'urn:fdc:peppol.eu:2017:poacc:billing:01:1.0'
    
    # Singapore country code
    COUNTRY_CODE = 'SG'
    
    # GST scheme ID for Singapore
    TAX_SCHEME_ID = 'GST'
    
    @staticmethod
    def generate(invoice) -> str:
        """
        Generate UBL 2.1 XML for an invoice.
        
        Args:
            invoice: accounting.Invoice instance
            
        Returns:
            UBL XML string
        """
        # Register namespaces for cleaner output
        for prefix, uri in NAMESPACES.items():
            ET.register_namespace(prefix, uri)
        
        # Create root Invoice element
        root = ET.Element(
            '{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}Invoice',
            {
                'xmlns': NAMESPACES['ubl'],
                'xmlns:cac': NAMESPACES['cac'],
                'xmlns:cbc': NAMESPACES['cbc'],
            }
        )
        
        # Add required elements
        UBLGenerator._add_header(root, invoice)
        UBLGenerator._add_supplier_party(root, invoice)
        UBLGenerator._add_customer_party(root, invoice)
        UBLGenerator._add_tax_total(root, invoice)
        UBLGenerator._add_monetary_total(root, invoice)
        UBLGenerator._add_invoice_lines(root, invoice)
        
        # Generate XML string
        ET.indent(root, space='  ')
        xml_str = ET.tostring(root, encoding='unicode', xml_declaration=True)
        
        return xml_str
    
    @staticmethod
    def _add_header(root: ET.Element, invoice) -> None:
        """Add invoice header elements."""
        # Customization ID
        cbc_cust = ET.SubElement(root, '{%s}CustomizationID' % NAMESPACES['cbc'])
        cbc_cust.text = UBLGenerator.CUSTOMIZATION_ID
        
        # Profile ID
        cbc_prof = ET.SubElement(root, '{%s}ProfileID' % NAMESPACES['cbc'])
        cbc_prof.text = UBLGenerator.PROFILE_ID
        
        # Invoice ID
        cbc_id = ET.SubElement(root, '{%s}ID' % NAMESPACES['cbc'])
        cbc_id.text = invoice.invoice_number
        
        # Issue Date
        cbc_date = ET.SubElement(root, '{%s}IssueDate' % NAMESPACES['cbc'])
        cbc_date.text = invoice.invoice_date.isoformat()
        
        # Due Date
        if invoice.due_date:
            cbc_due = ET.SubElement(root, '{%s}DueDate' % NAMESPACES['cbc'])
            cbc_due.text = invoice.due_date.isoformat()
        
        # Invoice Type Code (380 = Commercial Invoice)
        cbc_type = ET.SubElement(root, '{%s}InvoiceTypeCode' % NAMESPACES['cbc'])
        cbc_type.text = '380'
        
        # Document Currency
        cbc_curr = ET.SubElement(root, '{%s}DocumentCurrencyCode' % NAMESPACES['cbc'])
        cbc_curr.text = invoice.currency or 'SGD'
    
    @staticmethod
    def _add_supplier_party(root: ET.Element, invoice) -> None:
        """Add supplier (seller) party."""
        cac_sup = ET.SubElement(root, '{%s}AccountingSupplierParty' % NAMESPACES['cac'])
        cac_party = ET.SubElement(cac_sup, '{%s}Party' % NAMESPACES['cac'])
        
        # Endpoint ID (PEPPOL participant ID)
        company = invoice.company
        cbc_endpoint = ET.SubElement(cac_party, '{%s}EndpointID' % NAMESPACES['cbc'])
        cbc_endpoint.set('schemeID', '0195')  # Singapore UEN scheme
        cbc_endpoint.text = company.uen or ''
        
        # Party Name
        cac_name = ET.SubElement(cac_party, '{%s}PartyName' % NAMESPACES['cac'])
        cbc_name = ET.SubElement(cac_name, '{%s}Name' % NAMESPACES['cbc'])
        cbc_name.text = company.name
        
        # Postal Address
        UBLGenerator._add_address(cac_party, company)
        
        # Tax Registration (GST number)
        cac_tax = ET.SubElement(cac_party, '{%s}PartyTaxScheme' % NAMESPACES['cac'])
        cbc_tax_id = ET.SubElement(cac_tax, '{%s}CompanyID' % NAMESPACES['cbc'])
        cbc_tax_id.text = company.gst_registration_number or company.uen or ''
        
        cac_scheme = ET.SubElement(cac_tax, '{%s}TaxScheme' % NAMESPACES['cac'])
        cbc_scheme_id = ET.SubElement(cac_scheme, '{%s}ID' % NAMESPACES['cbc'])
        cbc_scheme_id.text = UBLGenerator.TAX_SCHEME_ID
    
    @staticmethod
    def _add_customer_party(root: ET.Element, invoice) -> None:
        """Add customer (buyer) party."""
        cac_cust = ET.SubElement(root, '{%s}AccountingCustomerParty' % NAMESPACES['cac'])
        cac_party = ET.SubElement(cac_cust, '{%s}Party' % NAMESPACES['cac'])
        
        customer = invoice.customer
        
        # Endpoint ID
        cbc_endpoint = ET.SubElement(cac_party, '{%s}EndpointID' % NAMESPACES['cbc'])
        cbc_endpoint.set('schemeID', '0195')
        cbc_endpoint.text = customer.company_uen or customer.email
        
        # Party Name
        cac_name = ET.SubElement(cac_party, '{%s}PartyName' % NAMESPACES['cac'])
        cbc_name = ET.SubElement(cac_name, '{%s}Name' % NAMESPACES['cbc'])
        cbc_name.text = customer.company_name or f"{customer.first_name} {customer.last_name}"
        
        # Contact
        cac_contact = ET.SubElement(cac_party, '{%s}Contact' % NAMESPACES['cac'])
        cbc_email = ET.SubElement(cac_contact, '{%s}ElectronicMail' % NAMESPACES['cbc'])
        cbc_email.text = customer.email
    
    @staticmethod
    def _add_address(party: ET.Element, entity) -> None:
        """Add postal address to a party."""
        cac_addr = ET.SubElement(party, '{%s}PostalAddress' % NAMESPACES['cac'])
        
        if hasattr(entity, 'address_line1') and entity.address_line1:
            cbc_line = ET.SubElement(cac_addr, '{%s}StreetName' % NAMESPACES['cbc'])
            cbc_line.text = entity.address_line1
        
        if hasattr(entity, 'city') and entity.city:
            cbc_city = ET.SubElement(cac_addr, '{%s}CityName' % NAMESPACES['cbc'])
            cbc_city.text = entity.city
        
        if hasattr(entity, 'postal_code') and entity.postal_code:
            cbc_postal = ET.SubElement(cac_addr, '{%s}PostalZone' % NAMESPACES['cbc'])
            cbc_postal.text = entity.postal_code
        
        cac_country = ET.SubElement(cac_addr, '{%s}Country' % NAMESPACES['cac'])
        cbc_code = ET.SubElement(cac_country, '{%s}IdentificationCode' % NAMESPACES['cbc'])
        cbc_code.text = UBLGenerator.COUNTRY_CODE
    
    @staticmethod
    def _add_tax_total(root: ET.Element, invoice) -> None:
        """Add tax total."""
        cac_tax = ET.SubElement(root, '{%s}TaxTotal' % NAMESPACES['cac'])
        
        cbc_amount = ET.SubElement(cac_tax, '{%s}TaxAmount' % NAMESPACES['cbc'])
        cbc_amount.set('currencyID', invoice.currency or 'SGD')
        cbc_amount.text = str(invoice.tax_amount)
        
        # Tax subtotal
        cac_subtotal = ET.SubElement(cac_tax, '{%s}TaxSubtotal' % NAMESPACES['cac'])
        
        cbc_taxable = ET.SubElement(cac_subtotal, '{%s}TaxableAmount' % NAMESPACES['cbc'])
        cbc_taxable.set('currencyID', invoice.currency or 'SGD')
        cbc_taxable.text = str(invoice.subtotal)
        
        cbc_tax_amt = ET.SubElement(cac_subtotal, '{%s}TaxAmount' % NAMESPACES['cbc'])
        cbc_tax_amt.set('currencyID', invoice.currency or 'SGD')
        cbc_tax_amt.text = str(invoice.tax_amount)
        
        # Tax Category
        cac_cat = ET.SubElement(cac_subtotal, '{%s}TaxCategory' % NAMESPACES['cac'])
        
        cbc_cat_id = ET.SubElement(cac_cat, '{%s}ID' % NAMESPACES['cbc'])
        cbc_cat_id.text = 'S'  # Standard rate
        
        cbc_percent = ET.SubElement(cac_cat, '{%s}Percent' % NAMESPACES['cbc'])
        cbc_percent.text = '9'  # 9% GST
        
        cac_scheme = ET.SubElement(cac_cat, '{%s}TaxScheme' % NAMESPACES['cac'])
        cbc_scheme_id = ET.SubElement(cac_scheme, '{%s}ID' % NAMESPACES['cbc'])
        cbc_scheme_id.text = UBLGenerator.TAX_SCHEME_ID
    
    @staticmethod
    def _add_monetary_total(root: ET.Element, invoice) -> None:
        """Add monetary totals."""
        cac_total = ET.SubElement(root, '{%s}LegalMonetaryTotal' % NAMESPACES['cac'])
        
        currency = invoice.currency or 'SGD'
        
        # Line Extension Amount (subtotal)
        cbc_line = ET.SubElement(cac_total, '{%s}LineExtensionAmount' % NAMESPACES['cbc'])
        cbc_line.set('currencyID', currency)
        cbc_line.text = str(invoice.subtotal)
        
        # Tax Exclusive Amount
        cbc_excl = ET.SubElement(cac_total, '{%s}TaxExclusiveAmount' % NAMESPACES['cbc'])
        cbc_excl.set('currencyID', currency)
        cbc_excl.text = str(invoice.subtotal)
        
        # Tax Inclusive Amount (total)
        cbc_incl = ET.SubElement(cac_total, '{%s}TaxInclusiveAmount' % NAMESPACES['cbc'])
        cbc_incl.set('currencyID', currency)
        cbc_incl.text = str(invoice.total_amount)
        
        # Payable Amount
        cbc_payable = ET.SubElement(cac_total, '{%s}PayableAmount' % NAMESPACES['cbc'])
        cbc_payable.set('currencyID', currency)
        cbc_payable.text = str(invoice.amount_due or invoice.total_amount)
    
    @staticmethod
    def _add_invoice_lines(root: ET.Element, invoice) -> None:
        """Add invoice line items."""
        for idx, line in enumerate(invoice.lines.all(), start=1):
            cac_line = ET.SubElement(root, '{%s}InvoiceLine' % NAMESPACES['cac'])
            
            # Line ID
            cbc_id = ET.SubElement(cac_line, '{%s}ID' % NAMESPACES['cbc'])
            cbc_id.text = str(idx)
            
            # Quantity
            cbc_qty = ET.SubElement(cac_line, '{%s}InvoicedQuantity' % NAMESPACES['cbc'])
            cbc_qty.set('unitCode', line.unit_of_measure or 'EA')
            cbc_qty.text = str(line.quantity)
            
            # Line Extension Amount
            cbc_amount = ET.SubElement(cac_line, '{%s}LineExtensionAmount' % NAMESPACES['cbc'])
            cbc_amount.set('currencyID', invoice.currency or 'SGD')
            cbc_amount.text = str(line.line_total)
            
            # Item
            cac_item = ET.SubElement(cac_line, '{%s}Item' % NAMESPACES['cac'])
            
            cbc_desc = ET.SubElement(cac_item, '{%s}Description' % NAMESPACES['cbc'])
            cbc_desc.text = line.description
            
            cbc_name = ET.SubElement(cac_item, '{%s}Name' % NAMESPACES['cbc'])
            cbc_name.text = line.description[:100]
            
            # Classified Tax Category
            cac_tax = ET.SubElement(cac_item, '{%s}ClassifiedTaxCategory' % NAMESPACES['cac'])
            
            cbc_cat_id = ET.SubElement(cac_tax, '{%s}ID' % NAMESPACES['cbc'])
            cbc_cat_id.text = UBLGenerator._get_tax_category(line.gst_code or 'SR')
            
            cbc_percent = ET.SubElement(cac_tax, '{%s}Percent' % NAMESPACES['cbc'])
            cbc_percent.text = str(line.tax_rate or 9)
            
            cac_scheme = ET.SubElement(cac_tax, '{%s}TaxScheme' % NAMESPACES['cac'])
            cbc_scheme_id = ET.SubElement(cac_scheme, '{%s}ID' % NAMESPACES['cbc'])
            cbc_scheme_id.text = UBLGenerator.TAX_SCHEME_ID
            
            # Price
            cac_price = ET.SubElement(cac_line, '{%s}Price' % NAMESPACES['cac'])
            
            cbc_price = ET.SubElement(cac_price, '{%s}PriceAmount' % NAMESPACES['cbc'])
            cbc_price.set('currencyID', invoice.currency or 'SGD')
            cbc_price.text = str(line.unit_price)
    
    @staticmethod
    def _get_tax_category(gst_code: str) -> str:
        """Map GST code to PEPPOL tax category."""
        mapping = {
            'SR': 'S',  # Standard rate
            'ZR': 'Z',  # Zero rate
            'ES': 'E',  # Exempt
            'OS': 'O',  # Out of scope
        }
        return mapping.get(gst_code, 'S')
