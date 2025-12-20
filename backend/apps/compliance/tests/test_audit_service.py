"""
Audit Service tests.
"""
import pytest
import uuid

from apps.compliance.models import AuditLog
from apps.compliance.services import AuditService
from apps.accounts.tests.factories import CompanyFactory, UserFactory


@pytest.mark.django_db
class TestAuditServiceLogChange:
    """Tests for AuditService log_change method."""
    
    def test_log_change_creates_entry(self):
        """Test that log_change creates an audit entry."""
        company = CompanyFactory()
        user = UserFactory()
        
        log = AuditService.log_change(
            action='CREATE',
            resource_type='commerce.order',
            resource_id=uuid.uuid4(),
            new_values={'status': 'pending'},
            user=user,
            company=company,
        )
        
        assert log.id is not None
        assert log.action == 'CREATE'
        assert log.user == user
        assert log.company == company
    
    def test_log_change_with_old_values(self):
        """Test logging with old values."""
        log = AuditService.log_change(
            action='UPDATE',
            resource_type='commerce.order',
            resource_id=uuid.uuid4(),
            old_values={'status': 'pending'},
            new_values={'status': 'confirmed'},
        )
        
        assert log.old_values == {'status': 'pending'}
        assert log.new_values == {'status': 'confirmed'}


@pytest.mark.django_db
class TestAuditServiceModelLogging:
    """Tests for model-level audit logging."""
    
    def test_log_model_create(self):
        """Test logging model creation."""
        company = CompanyFactory()
        
        log = AuditService.log_model_create(company)
        
        assert log.action == 'CREATE'
        assert 'company' in log.resource_type
        assert log.resource_id == company.id
    
    def test_log_model_delete(self):
        """Test logging model deletion."""
        company = CompanyFactory()
        
        log = AuditService.log_model_delete(company)
        
        assert log.action == 'DELETE'
        assert log.old_values != {}


@pytest.mark.django_db
class TestAuditServiceHistory:
    """Tests for audit history retrieval."""
    
    def test_get_history(self):
        """Test retrieving history for a resource."""
        resource_id = uuid.uuid4()
        
        AuditService.log_change(
            action='CREATE',
            resource_type='test.model',
            resource_id=resource_id,
            new_values={'version': 1},
        )
        AuditService.log_change(
            action='UPDATE',
            resource_type='test.model',
            resource_id=resource_id,
            old_values={'version': 1},
            new_values={'version': 2},
        )
        
        history = AuditService.get_history('test.model', resource_id)
        
        assert len(history) == 2
    
    def test_get_user_activity(self):
        """Test retrieving user activity."""
        user = UserFactory()
        
        AuditService.log_change(
            action='CREATE',
            resource_type='test.model',
            resource_id=uuid.uuid4(),
            user=user,
        )
        
        activity = AuditService.get_user_activity(user.id)
        
        assert len(activity) >= 1
