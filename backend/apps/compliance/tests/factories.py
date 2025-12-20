"""
Factory Boy factories for compliance tests.
"""
import factory
from factory.django import DjangoModelFactory
from decimal import Decimal
from datetime import date, timedelta
import uuid

from django.utils import timezone

from apps.accounts.tests.factories import CompanyFactory, UserFactory
from apps.commerce.tests.factories import CustomerFactory
from apps.compliance.models import GSTReturn, DataConsent, DataAccessRequest, AuditLog


class GSTReturnFactory(DjangoModelFactory):
    """Factory for GSTReturn model."""
    
    class Meta:
        model = GSTReturn
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    period_start = factory.LazyFunction(lambda: date(2024, 1, 1))
    period_end = factory.LazyFunction(lambda: date(2024, 3, 31))
    quarter = 1
    year = 2024
    
    box_1 = Decimal('10000.00')
    box_2 = Decimal('5000.00')
    box_3 = Decimal('1000.00')
    box_4 = Decimal('16000.00')  # 1+2+3
    box_5 = Decimal('8000.00')
    box_6 = Decimal('900.00')  # GST on box_1
    box_7 = Decimal('720.00')  # GST on purchases
    box_8 = Decimal('180.00')  # 6-7
    
    status = 'draft'


class DraftGSTReturnFactory(GSTReturnFactory):
    """Factory for draft GST returns."""
    status = 'draft'


class ValidatedGSTReturnFactory(GSTReturnFactory):
    """Factory for validated GST returns."""
    status = 'validated'


class SubmittedGSTReturnFactory(GSTReturnFactory):
    """Factory for submitted GST returns."""
    status = 'submitted'
    submission_date = factory.LazyFunction(date.today)
    submitted_by = factory.SubFactory(UserFactory)


class DataConsentFactory(DjangoModelFactory):
    """Factory for DataConsent model."""
    
    class Meta:
        model = DataConsent
    
    id = factory.LazyFunction(uuid.uuid4)
    customer = factory.SubFactory(CustomerFactory)
    consent_type = 'marketing'
    is_granted = True
    source = 'registration'
    ip_address = '127.0.0.1'
    user_agent = 'Test Browser'
    consent_timestamp = factory.LazyFunction(timezone.now)


class MarketingConsentFactory(DataConsentFactory):
    """Factory for marketing consent."""
    consent_type = 'marketing'


class AnalyticsConsentFactory(DataConsentFactory):
    """Factory for analytics consent."""
    consent_type = 'analytics'


class ConsentWithdrawalFactory(DataConsentFactory):
    """Factory for consent withdrawal."""
    is_granted = False


class DataAccessRequestFactory(DjangoModelFactory):
    """Factory for DataAccessRequest model."""
    
    class Meta:
        model = DataAccessRequest
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    customer = factory.SubFactory(CustomerFactory)
    request_type = 'access'
    status = 'pending'
    requested_at = factory.LazyFunction(timezone.now)
    due_date = factory.LazyFunction(lambda: date.today() + timedelta(days=30))


class AccessRequestFactory(DataAccessRequestFactory):
    """Factory for data access requests."""
    request_type = 'access'


class DeletionRequestFactory(DataAccessRequestFactory):
    """Factory for data deletion requests."""
    request_type = 'deletion'


class OverdueRequestFactory(DataAccessRequestFactory):
    """Factory for overdue requests."""
    due_date = factory.LazyFunction(lambda: date.today() - timedelta(days=5))


class AuditLogFactory(DjangoModelFactory):
    """Factory for AuditLog model."""
    
    class Meta:
        model = AuditLog
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    user = factory.SubFactory(UserFactory)
    action = 'CREATE'
    resource_type = 'commerce.order'
    resource_id = factory.LazyFunction(uuid.uuid4)
    old_values = factory.LazyFunction(dict)
    new_values = factory.LazyFunction(lambda: {'status': 'pending'})
    ip_address = '127.0.0.1'


class CreateAuditLogFactory(AuditLogFactory):
    """Factory for CREATE audit logs."""
    action = 'CREATE'
    old_values = {}
    new_values = factory.LazyFunction(lambda: {'id': str(uuid.uuid4())})


class UpdateAuditLogFactory(AuditLogFactory):
    """Factory for UPDATE audit logs."""
    action = 'UPDATE'
    old_values = factory.LazyFunction(lambda: {'status': 'pending'})
    new_values = factory.LazyFunction(lambda: {'status': 'confirmed'})


class DeleteAuditLogFactory(AuditLogFactory):
    """Factory for DELETE audit logs."""
    action = 'DELETE'
    old_values = factory.LazyFunction(lambda: {'id': str(uuid.uuid4())})
    new_values = {}
