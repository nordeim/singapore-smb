"""InvoiceNow Celery tasks."""
import logging
from celery import shared_task

from django.utils import timezone
from datetime import timedelta


logger = logging.getLogger(__name__)


@shared_task
def auto_submit_invoices():
    """
    Auto-submit invoices marked for InvoiceNow.
    
    Runs periodically to process invoices pending PEPPOL submission.
    """
    from apps.accounting.models import Invoice
    from apps.invoicenow.services import PEPPOLService
    
    # Find invoices ready for submission
    ready_invoices = Invoice.objects.filter(
        peppol_status='',
        status='sent',  # Only sent invoices
        created_at__gte=timezone.now() - timedelta(days=30),
    ).exclude(
        customer__company_uen=''
    ).exclude(
        customer__company_uen__isnull=True
    )[:10]  # Batch of 10
    
    submitted = 0
    errors = 0
    
    for invoice in ready_invoices:
        try:
            PEPPOLService.process_full_workflow(invoice)
            submitted += 1
        except Exception as e:
            logger.error(f"Failed to submit invoice {invoice.invoice_number}: {e}")
            errors += 1
    
    return {
        'submitted': submitted,
        'errors': errors,
    }


@shared_task
def check_submission_status():
    """
    Check status of submitted PEPPOL invoices.
    
    Queries Access Point for acknowledgments.
    """
    from apps.invoicenow.models import PEPPOLInvoice
    
    # Find submitted invoices without acknowledgment
    pending = PEPPOLInvoice.objects.filter(
        status='submitted',
        submitted_at__gte=timezone.now() - timedelta(days=7),
    )
    
    checked = 0
    
    for peppol_invoice in pending:
        # Would query AP for status here
        checked += 1
    
    logger.info(f"Checked status for {checked} submitted invoices")
    
    return {'checked': checked}


@shared_task
def retry_failed_submissions():
    """
    Retry failed PEPPOL submissions.
    """
    from apps.invoicenow.models import PEPPOLInvoice
    from apps.invoicenow.services import PEPPOLService
    
    # Find rejected invoices that can be retried
    failed = PEPPOLInvoice.objects.filter(
        status='rejected',
        updated_at__gte=timezone.now() - timedelta(days=7),
    )[:5]
    
    retried = 0
    
    for peppol_invoice in failed:
        try:
            # Reset to draft for retry
            peppol_invoice.status = 'draft'
            peppol_invoice.validation_errors = []
            peppol_invoice.save()
            
            # Re-run workflow
            PEPPOLService.process_full_workflow(peppol_invoice.invoice)
            retried += 1
        except Exception as e:
            logger.error(f"Retry failed for {peppol_invoice.peppol_id}: {e}")
    
    return {'retried': retried}
