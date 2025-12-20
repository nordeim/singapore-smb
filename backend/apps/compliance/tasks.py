"""
Compliance Celery tasks.

Provides periodic tasks for:
- Overdue data access request alerts
- GST filing reminders
- Data retention enforcement
"""
import logging
from datetime import date, timedelta

from celery import shared_task
from django.utils import timezone

from apps.compliance.models import DataAccessRequest, GSTReturn


logger = logging.getLogger(__name__)


@shared_task
def check_overdue_access_requests():
    """
    Check for overdue PDPA data access requests.
    
    Runs daily to identify requests approaching or past SLA.
    """
    today = date.today()
    warning_threshold = today + timedelta(days=5)
    
    # Find at-risk requests (due within 5 days)
    at_risk = DataAccessRequest.objects.filter(
        status__in=['pending', 'processing'],
        due_date__lte=warning_threshold,
        due_date__gte=today,
    ).count()
    
    # Find overdue requests
    overdue = DataAccessRequest.objects.filter(
        status__in=['pending', 'processing'],
        due_date__lt=today,
    ).count()
    
    if at_risk > 0:
        logger.warning(f"{at_risk} data access requests at risk of SLA breach")
    
    if overdue > 0:
        logger.error(f"{overdue} data access requests are OVERDUE")
    
    return {
        'at_risk': at_risk,
        'overdue': overdue,
        'checked_at': timezone.now().isoformat(),
    }


@shared_task
def send_gst_filing_reminder():
    """
    Send reminders for quarterly GST filing.
    
    Runs weekly, sends alerts when approaching quarter end.
    """
    today = date.today()
    current_month = today.month
    current_year = today.year
    
    # Determine current quarter
    current_quarter = (current_month - 1) // 3 + 1
    
    # Check if we're in a filing month (last month of quarter)
    filing_months = [3, 6, 9, 12]
    is_filing_month = current_month in filing_months
    
    if not is_filing_month:
        return {'reminder_sent': False, 'reason': 'Not a filing month'}
    
    # Find companies without submitted returns for this quarter
    from apps.accounts.models import Company
    
    companies_needing_filing = []
    
    for company in Company.objects.filter(is_active=True, deleted_at__isnull=True):
        existing_return = GSTReturn.objects.filter(
            company=company,
            year=current_year,
            quarter=current_quarter,
            status__in=['submitted', 'accepted'],
        ).exists()
        
        if not existing_return:
            companies_needing_filing.append(company.name)
            logger.info(
                f"GST filing reminder: {company.name} needs Q{current_quarter}/{current_year} return"
            )
    
    return {
        'reminder_sent': True,
        'quarter': current_quarter,
        'year': current_year,
        'companies_pending': len(companies_needing_filing),
    }


@shared_task
def enforce_data_retention():
    """
    Enforce data retention policy.
    
    Anonymizes customers past their retention date.
    Runs monthly.
    """
    from apps.commerce.models import Customer
    from apps.compliance.services import PDPAService
    
    today = date.today()
    
    # Find customers past retention date
    customers_to_anonymize = Customer.objects.filter(
        data_retention_until__lt=today,
        email__contains='@',  # Not already anonymized
    ).exclude(
        email__contains='@anonymized.local'
    )
    
    count = 0
    for customer in customers_to_anonymize:
        try:
            PDPAService.anonymize_customer(customer)
            count += 1
        except Exception as e:
            logger.error(f"Failed to anonymize customer {customer.id}: {e}")
    
    if count > 0:
        logger.info(f"Anonymized {count} customers per data retention policy")
    
    return {
        'anonymized_count': count,
        'checked_at': timezone.now().isoformat(),
    }
