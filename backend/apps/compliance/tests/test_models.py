"""
Model tests for compliance app.
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta

from django.utils import timezone

from apps.compliance.models import GSTReturn, DataConsent, DataAccessRequest, AuditLog
from apps.compliance.tests.factories import (
    GSTReturnFactory, ValidatedGSTReturnFactory, SubmittedGSTReturnFactory,
    DataConsentFactory, DataAccessRequestFactory, OverdueRequestFactory,
    AuditLogFactory,
)


@pytest.mark.django_db
class TestGSTReturn:
    """Tests for GSTReturn model."""
    
    def test_create_gst_return(self):
        """Test creating a GST return."""
        gst_return = GSTReturnFactory()
        
        assert gst_return.id is not None
        assert gst_return.quarter == 1
        assert gst_return.year == 2024
        assert gst_return.status == 'draft'
    
    def test_validate_boxes_correct(self):
        """Test box validation with correct values."""
        gst_return = GSTReturnFactory(
            box_1=Decimal('10000.00'),
            box_2=Decimal('5000.00'),
            box_3=Decimal('1000.00'),
            box_4=Decimal('16000.00'),
            box_6=Decimal('900.00'),
            box_7=Decimal('720.00'),
            box_8=Decimal('180.00'),
        )
        
        is_valid, errors = gst_return.validate_boxes()
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_boxes_incorrect_box_4(self):
        """Test box validation with incorrect box 4."""
        gst_return = GSTReturnFactory(
            box_1=Decimal('10000.00'),
            box_2=Decimal('5000.00'),
            box_3=Decimal('1000.00'),
            box_4=Decimal('15000.00'),  # Wrong: should be 16000
        )
        
        is_valid, errors = gst_return.validate_boxes()
        
        assert is_valid is False
        assert len(errors) >= 1
        assert 'Box 4' in errors[0]
    
    def test_validate_boxes_incorrect_box_8(self):
        """Test box validation with incorrect box 8."""
        gst_return = GSTReturnFactory(
            box_6=Decimal('900.00'),
            box_7=Decimal('720.00'),
            box_8=Decimal('200.00'),  # Wrong: should be 180
        )
        
        is_valid, errors = gst_return.validate_boxes()
        
        assert is_valid is False
        assert any('Box 8' in e for e in errors)
    
    def test_compute_boxes(self):
        """Test automatic box computation."""
        gst_return = GSTReturnFactory(
            box_1=Decimal('10000.00'),
            box_2=Decimal('5000.00'),
            box_3=Decimal('1000.00'),
            box_4=Decimal('0.00'),  # Will be computed
            box_6=Decimal('900.00'),
            box_7=Decimal('720.00'),
            box_8=Decimal('0.00'),  # Will be computed
        )
        
        gst_return.compute_boxes()
        
        assert gst_return.box_4 == Decimal('16000.00')
        assert gst_return.box_8 == Decimal('180.00')
    
    def test_can_submit_draft_false(self):
        """Test that draft returns cannot be submitted."""
        gst_return = GSTReturnFactory(status='draft')
        
        assert gst_return.can_submit() is False
    
    def test_can_submit_validated_true(self):
        """Test that validated returns can be submitted."""
        gst_return = ValidatedGSTReturnFactory()
        
        assert gst_return.can_submit() is True
    
    def test_mark_validated(self):
        """Test marking a return as validated."""
        gst_return = GSTReturnFactory()
        
        gst_return.mark_validated()
        
        assert gst_return.status == 'validated'
    
    def test_mark_submitted(self):
        """Test marking a return as submitted."""
        from apps.accounts.tests.factories import UserFactory
        
        gst_return = ValidatedGSTReturnFactory()
        user = UserFactory()
        
        gst_return.mark_submitted(submitted_by=user, iras_reference='IR123')
        
        assert gst_return.status == 'submitted'
        assert gst_return.submitted_by == user
        assert gst_return.iras_reference == 'IR123'
        assert gst_return.submission_date is not None
    
    def test_unique_company_year_quarter(self):
        """Test unique constraint on company-year-quarter."""
        gst_return = GSTReturnFactory()
        
        with pytest.raises(Exception):  # IntegrityError
            GSTReturnFactory(
                company=gst_return.company,
                year=gst_return.year,
                quarter=gst_return.quarter,
            )


@pytest.mark.django_db
class TestDataConsent:
    """Tests for DataConsent model."""
    
    def test_create_consent(self):
        """Test creating a consent record."""
        consent = DataConsentFactory()
        
        assert consent.id is not None
        assert consent.consent_type == 'marketing'
        assert consent.is_granted is True
    
    def test_consent_is_immutable(self):
        """Test that consent records cannot be updated."""
        consent = DataConsentFactory()
        consent.is_granted = False
        
        with pytest.raises(ValueError, match="immutable"):
            consent.save()
    
    def test_consent_cannot_be_deleted(self):
        """Test that consent records cannot be deleted."""
        consent = DataConsentFactory()
        
        with pytest.raises(ValueError, match="cannot be deleted"):
            consent.delete()
    
    def test_consent_str(self):
        """Test string representation."""
        consent = DataConsentFactory(
            consent_type='marketing',
            is_granted=True,
        )
        
        assert 'granted' in str(consent)
        assert 'marketing' in str(consent)


@pytest.mark.django_db
class TestDataAccessRequest:
    """Tests for DataAccessRequest model."""
    
    def test_create_request(self):
        """Test creating a data access request."""
        request = DataAccessRequestFactory()
        
        assert request.id is not None
        assert request.status == 'pending'
        assert request.due_date is not None
    
    def test_due_date_auto_calculated(self):
        """Test that due_date is auto-calculated to 30 days."""
        from apps.accounts.tests.factories import CompanyFactory
        from apps.commerce.tests.factories import CustomerFactory
        
        request = DataAccessRequest(
            company=CompanyFactory(),
            customer=CustomerFactory(),
            request_type='access',
        )
        request.save()
        
        expected_due = date.today() + timedelta(days=30)
        assert request.due_date == expected_due
    
    def test_is_overdue_false(self):
        """Test is_overdue for non-overdue request."""
        request = DataAccessRequestFactory()
        
        assert request.is_overdue is False
    
    def test_is_overdue_true(self):
        """Test is_overdue for overdue request."""
        request = OverdueRequestFactory()
        
        assert request.is_overdue is True
    
    def test_days_until_due(self):
        """Test days_until_due calculation."""
        request = DataAccessRequestFactory(
            due_date=date.today() + timedelta(days=15)
        )
        
        assert request.days_until_due == 15
    
    def test_sla_status_on_track(self):
        """Test SLA status for requests on track."""
        request = DataAccessRequestFactory(
            due_date=date.today() + timedelta(days=20)
        )
        
        assert request.sla_status == 'on_track'
    
    def test_sla_status_at_risk(self):
        """Test SLA status for at-risk requests."""
        request = DataAccessRequestFactory(
            due_date=date.today() + timedelta(days=3)
        )
        
        assert request.sla_status == 'at_risk'
    
    def test_sla_status_overdue(self):
        """Test SLA status for overdue requests."""
        request = OverdueRequestFactory()
        
        assert request.sla_status == 'overdue'
    
    def test_complete_request(self):
        """Test completing a request."""
        request = DataAccessRequestFactory()
        
        request.complete(notes='Data exported')
        
        assert request.status == 'completed'
        assert request.completed_at is not None
        assert request.response_notes == 'Data exported'
    
    def test_reject_request(self):
        """Test rejecting a request."""
        request = DataAccessRequestFactory()
        
        request.reject(reason='Invalid request')
        
        assert request.status == 'rejected'
        assert request.response_notes == 'Invalid request'


@pytest.mark.django_db
class TestAuditLog:
    """Tests for AuditLog model."""
    
    def test_create_audit_log(self):
        """Test creating an audit log."""
        log = AuditLogFactory()
        
        assert log.id is not None
        assert log.action == 'CREATE'
        assert log.resource_type == 'commerce.order'
    
    def test_audit_log_is_immutable(self):
        """Test that audit logs cannot be updated."""
        log = AuditLogFactory()
        log.action = 'DELETE'
        
        with pytest.raises(ValueError, match="immutable"):
            log.save()
    
    def test_audit_log_cannot_be_deleted(self):
        """Test that audit logs cannot be deleted."""
        log = AuditLogFactory()
        
        with pytest.raises(ValueError, match="cannot be deleted"):
            log.delete()
    
    def test_changes_for_create(self):
        """Test changes property for CREATE action."""
        log = AuditLogFactory(
            action='CREATE',
            old_values={},
            new_values={'status': 'pending', 'total': '100'},
        )
        
        changes = log.changes
        
        assert changes['status'] == (None, 'pending')
        assert changes['total'] == (None, '100')
    
    def test_changes_for_update(self):
        """Test changes property for UPDATE action."""
        log = AuditLogFactory(
            action='UPDATE',
            old_values={'status': 'pending'},
            new_values={'status': 'confirmed'},
        )
        
        changes = log.changes
        
        assert changes['status'] == ('pending', 'confirmed')
    
    def test_changes_for_delete(self):
        """Test changes property for DELETE action."""
        log = AuditLogFactory(
            action='DELETE',
            old_values={'id': '123'},
            new_values={},
        )
        
        changes = log.changes
        
        assert changes['id'] == ('123', None)
    
    def test_change_summary(self):
        """Test change summary generation."""
        log = AuditLogFactory(
            action='UPDATE',
            old_values={'status': 'pending'},
            new_values={'status': 'confirmed'},
        )
        
        summary = log.change_summary
        
        assert 'status' in summary
        assert 'pending' in summary
        assert 'confirmed' in summary
