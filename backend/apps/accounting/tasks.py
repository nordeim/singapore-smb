"""
Celery tasks for accounting module.
"""
from datetime import date
from celery import shared_task
import logging

from django.db import transaction


logger = logging.getLogger(__name__)


@shared_task(name='accounting.check_overdue_invoices')
def check_overdue_invoices():
    """
    Periodic task to check and update overdue invoice status.
    
    Run daily to mark invoices as overdue when past due date.
    """
    from apps.accounts.models import Company
    from apps.accounting.services import InvoiceService
    
    total_marked = 0
    
    for company in Company.objects.filter(is_active=True):
        count = InvoiceService.check_overdue_invoices(company)
        total_marked += count
    
    if total_marked > 0:
        logger.info(f"Marked {total_marked} invoices as overdue")
    
    return {'marked_overdue': total_marked}


@shared_task(name='accounting.prepare_gst_filing_reminder')
def prepare_gst_filing_reminder():
    """
    Periodic task to send GST filing reminders.
    
    Run weekly. Sends reminder when quarter end is within 7 days.
    """
    from apps.accounts.models import Company
    
    today = date.today()
    
    # Determine current quarter end
    quarter_ends = [
        date(today.year, 3, 31),
        date(today.year, 6, 30),
        date(today.year, 9, 30),
        date(today.year, 12, 31),
    ]
    
    upcoming_end = None
    for end_date in quarter_ends:
        if end_date >= today and (end_date - today).days <= 7:
            upcoming_end = end_date
            break
    
    if upcoming_end is None:
        logger.debug("No quarter end within 7 days")
        return {'reminders_sent': 0}
    
    # Get GST-registered companies
    companies = Company.objects.filter(
        is_active=True,
        gst_registered=True,
    )
    
    reminder_count = 0
    for company in companies:
        # TODO: Send actual notification/email
        logger.info(
            f"GST filing reminder for {company.name}: "
            f"Quarter ending {upcoming_end}"
        )
        reminder_count += 1
    
    return {'reminders_sent': reminder_count}


@shared_task(name='accounting.generate_daily_revenue_report')
def generate_daily_revenue_report(company_id: str, report_date: str = None):
    """
    Generate daily revenue report for a company.
    
    Args:
        company_id: UUID of company
        report_date: Date in YYYY-MM-DD format (default: yesterday)
    """
    from apps.accounts.models import Company
    from apps.commerce.models import Order
    from datetime import datetime, timedelta
    
    company = Company.objects.get(id=company_id)
    
    if report_date:
        target_date = datetime.strptime(report_date, '%Y-%m-%d').date()
    else:
        target_date = date.today() - timedelta(days=1)
    
    # Query completed orders for the date
    orders = Order.objects.filter(
        company=company,
        created_at__date=target_date,
        status__in=['confirmed', 'processing', 'shipped', 'delivered'],
    )
    
    # Aggregate
    from django.db.models import Sum, Count
    
    summary = orders.aggregate(
        order_count=Count('id'),
        total_revenue=Sum('total_amount'),
        total_gst=Sum('gst_amount'),
    )
    
    report = {
        'company_id': str(company_id),
        'date': target_date.isoformat(),
        'order_count': summary['order_count'] or 0,
        'total_revenue': str(summary['total_revenue'] or 0),
        'total_gst': str(summary['total_gst'] or 0),
    }
    
    logger.info(f"Daily revenue report for {company.name}: {report}")
    
    return report


@shared_task(name='accounting.generate_invoice_pdf')
def generate_invoice_pdf(invoice_id: str):
    """
    Generate PDF for an invoice.
    
    Args:
        invoice_id: UUID of invoice
        
    Returns:
        Path to generated PDF (placeholder)
    """
    from apps.accounting.models import Invoice
    
    invoice = Invoice.objects.get(id=invoice_id)
    
    # TODO: Implement actual PDF generation
    # For now, this is a placeholder
    
    logger.info(f"PDF generation requested for invoice {invoice.invoice_number}")
    
    return {
        'invoice_id': str(invoice_id),
        'invoice_number': invoice.invoice_number,
        'status': 'placeholder',
        'message': 'PDF generation not yet implemented',
    }


@shared_task(name='accounting.sync_account_balances')
def sync_account_balances(company_id: str):
    """
    Recalculate and sync account balances from journal entries.
    
    Use this task to fix any balance discrepancies.
    
    Args:
        company_id: UUID of company
    """
    from decimal import Decimal
    from django.db.models import Sum
    from apps.accounts.models import Company
    from apps.accounting.models import Account, JournalLine
    
    company = Company.objects.get(id=company_id)
    accounts = Account.objects.filter(company=company)
    
    updated_count = 0
    
    with transaction.atomic():
        for account in accounts:
            # Calculate balance from posted journal lines
            totals = JournalLine.objects.filter(
                account=account,
                journal_entry__status='posted',
            ).aggregate(
                total_debit=Sum('debit_amount'),
                total_credit=Sum('credit_amount'),
            )
            
            total_debit = totals['total_debit'] or Decimal('0.00')
            total_credit = totals['total_credit'] or Decimal('0.00')
            
            # Calculate new balance
            if account.is_debit_normal:
                new_balance = total_debit - total_credit
            else:
                new_balance = total_credit - total_debit
            
            # Update if different
            if account.current_balance != new_balance:
                account.current_balance = new_balance
                account.save(update_fields=['current_balance', 'updated_at'])
                updated_count += 1
                logger.info(
                    f"Updated balance for {account.code}: {new_balance}"
                )
    
    logger.info(f"Synced {updated_count} account balances for {company.name}")
    
    return {'updated_count': updated_count}
