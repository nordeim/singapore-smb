"""
PEPPOL Service for InvoiceNow integration.

Orchestrates UBL generation, signing, and AP submission.
"""
import logging
from typing import Optional, Dict, Any, Tuple, List
import uuid

from django.db import transaction
from django.conf import settings

from apps.invoicenow.models import PEPPOLInvoice, PEPPOLAcknowledgment
from apps.invoicenow.services.ubl_generator import UBLGenerator
from apps.invoicenow.services.xml_signer import XMLSigner


logger = logging.getLogger(__name__)


class PEPPOLService:
    """
    PEPPOL e-invoicing service for Singapore InvoiceNow.
    
    Provides:
    - Invoice preparation for PEPPOL
    - UBL generation
    - Digital signing
    - Access Point submission
    - Acknowledgment handling
    """
    
    @staticmethod
    def prepare_invoice(invoice) -> PEPPOLInvoice:
        """
        Prepare an accounting invoice for PEPPOL submission.
        
        Args:
            invoice: accounting.Invoice instance
            
        Returns:
            Created PEPPOLInvoice
        """
        # Check if already exists
        existing = PEPPOLInvoice.objects.filter(invoice=invoice).first()
        if existing:
            return existing
        
        # Generate UBL XML
        xml_content = UBLGenerator.generate(invoice)
        
        # Create PEPPOL invoice record
        peppol_invoice = PEPPOLInvoice.objects.create(
            invoice=invoice,
            peppol_id=f"SGPEPPOL-{uuid.uuid4().hex[:16].upper()}",
            sender_endpoint=invoice.company.uen or '',
            receiver_endpoint=invoice.customer.company_uen or invoice.customer.email,
            xml_document=xml_content,
            status='draft',
        )
        
        logger.info(f"Prepared PEPPOL invoice for {invoice.invoice_number}")
        
        return peppol_invoice
    
    @staticmethod
    def validate_invoice(peppol_invoice: PEPPOLInvoice) -> Tuple[bool, List[str]]:
        """
        Validate a PEPPOL invoice against BIS Billing 3.0 rules.
        
        Args:
            peppol_invoice: PEPPOLInvoice to validate
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        invoice = peppol_invoice.invoice
        
        # Required fields validation
        if not invoice.invoice_number:
            errors.append("Invoice number is required")
        
        if not invoice.invoice_date:
            errors.append("Invoice date is required")
        
        if not invoice.customer:
            errors.append("Customer is required")
        
        if not invoice.company.uen:
            errors.append("Supplier UEN is required")
        
        # Must have at least one line
        if invoice.lines.count() == 0:
            errors.append("At least one invoice line is required")
        
        # Check amounts
        if invoice.total_amount <= 0:
            errors.append("Invoice total must be positive")
        
        if errors:
            peppol_invoice.validation_errors = errors
            peppol_invoice.save(update_fields=['validation_errors'])
            return False, errors
        
        # Mark as validated
        if peppol_invoice.status == 'draft':
            peppol_invoice.mark_validated()
        
        return True, []
    
    @staticmethod
    def sign_invoice(peppol_invoice: PEPPOLInvoice) -> PEPPOLInvoice:
        """
        Sign PEPPOL invoice XML.
        
        Args:
            peppol_invoice: Validated PEPPOLInvoice
            
        Returns:
            Signed PEPPOLInvoice
        """
        if peppol_invoice.status != 'validated':
            raise ValueError("Invoice must be validated before signing")
        
        # Sign XML
        signed_xml = XMLSigner.sign(peppol_invoice.xml_document)
        
        # Extract signature
        signature = XMLSigner.extract_signature(signed_xml) or ''
        
        # Update record
        peppol_invoice.xml_document = signed_xml
        peppol_invoice.mark_signed(signature)
        
        logger.info(f"Signed PEPPOL invoice {peppol_invoice.peppol_id}")
        
        return peppol_invoice
    
    @staticmethod
    def submit_invoice(peppol_invoice: PEPPOLInvoice) -> PEPPOLInvoice:
        """
        Submit signed invoice to Access Point.
        
        Args:
            peppol_invoice: Signed PEPPOLInvoice
            
        Returns:
            Submitted PEPPOLInvoice
        """
        if peppol_invoice.status != 'signed':
            raise ValueError("Invoice must be signed before submission")
        
        # Get AP configuration
        ap_url = getattr(settings, 'PEPPOL_AP_URL', '')
        ap_key = getattr(settings, 'PEPPOL_AP_KEY', '')
        
        if not ap_url or not ap_key:
            logger.warning("PEPPOL Access Point not configured")
            raise ValueError("PEPPOL Access Point not configured")
        
        try:
            import httpx
            
            response = httpx.post(
                f'{ap_url}/documents',
                headers={
                    'Authorization': f'Bearer {ap_key}',
                    'Content-Type': 'application/xml',
                },
                content=peppol_invoice.xml_document.encode('utf-8'),
                timeout=60.0,
            )
            
            if response.status_code not in [200, 201, 202]:
                logger.error(f"AP submission failed: {response.text}")
                raise Exception(f"AP error: {response.status_code}")
            
            result = response.json()
            reference = result.get('reference', str(uuid.uuid4()))
            
            # Update status
            peppol_invoice.mark_submitted(
                provider=ap_url.split('/')[2],  # Extract domain
                reference=reference,
            )
            
            logger.info(
                f"Submitted PEPPOL invoice {peppol_invoice.peppol_id} "
                f"with reference {reference}"
            )
            
            return peppol_invoice
            
        except ImportError:
            raise ValueError("httpx package required for AP submission")
    
    @staticmethod
    def process_full_workflow(invoice) -> PEPPOLInvoice:
        """
        Run full workflow: prepare, validate, sign, submit.
        
        Args:
            invoice: accounting.Invoice
            
        Returns:
            Submitted PEPPOLInvoice
        """
        with transaction.atomic():
            # Prepare
            peppol_invoice = PEPPOLService.prepare_invoice(invoice)
            
            # Validate
            is_valid, errors = PEPPOLService.validate_invoice(peppol_invoice)
            if not is_valid:
                raise ValueError(f"Validation failed: {errors}")
            
            # Sign
            peppol_invoice = PEPPOLService.sign_invoice(peppol_invoice)
            
            # Submit
            peppol_invoice = PEPPOLService.submit_invoice(peppol_invoice)
            
            return peppol_invoice
    
    @staticmethod
    def process_acknowledgment(
        peppol_id: str,
        ack_type: str,
        response_code: str,
        description: str,
        payload: Dict[str, Any] = None,
    ) -> PEPPOLAcknowledgment:
        """
        Process an acknowledgment from Access Point.
        
        Args:
            peppol_id: PEPPOL document ID
            ack_type: delivery, application, or error
            response_code: Response code
            description: Response description
            payload: Full response payload
            
        Returns:
            Created PEPPOLAcknowledgment
        """
        peppol_invoice = PEPPOLInvoice.objects.get(peppol_id=peppol_id)
        
        ack = PEPPOLAcknowledgment.objects.create(
            peppol_invoice=peppol_invoice,
            acknowledgment_type=ack_type,
            response_code=response_code,
            response_description=description,
            response_payload=payload or {},
        )
        
        # Update invoice status based on acknowledgment
        if ack_type == 'application' and ack.is_success:
            peppol_invoice.mark_acknowledged()
        elif ack_type == 'error':
            peppol_invoice.mark_rejected([description])
        
        logger.info(f"Processed {ack_type} acknowledgment for {peppol_id}")
        
        return ack
    
    @staticmethod
    def get_submission_status(invoice) -> Dict[str, Any]:
        """
        Get PEPPOL submission status for an invoice.
        
        Args:
            invoice: accounting.Invoice
            
        Returns:
            Status information dict
        """
        peppol_invoice = PEPPOLInvoice.objects.filter(invoice=invoice).first()
        
        if not peppol_invoice:
            return {
                'exists': False,
                'status': None,
                'peppol_id': None,
            }
        
        acks = peppol_invoice.acknowledgments.all()
        
        return {
            'exists': True,
            'status': peppol_invoice.status,
            'peppol_id': peppol_invoice.peppol_id,
            'submitted_at': peppol_invoice.submitted_at.isoformat() if peppol_invoice.submitted_at else None,
            'acknowledgments': [
                {
                    'type': ack.acknowledgment_type,
                    'code': ack.response_code,
                    'description': ack.response_description,
                    'received_at': ack.received_at.isoformat(),
                }
                for ack in acks
            ],
        }
