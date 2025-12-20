"""
GST Return Service tests.
"""
import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import patch, MagicMock

from apps.compliance.models import GSTReturn
from apps.compliance.services import GSTReturnService
from apps.compliance.tests.factories import (
    GSTReturnFactory, ValidatedGSTReturnFactory,
)
from apps.accounts.tests.factories import CompanyFactory, UserFactory


@pytest.mark.django_db
class TestGSTReturnServicePrepare:
    """Tests for GSTReturnService.prepare_return."""
    
    @patch('apps.compliance.services.gst_return_service.GSTEngine')
    def test_prepare_return_creates_record(self, mock_gst_engine):
        """Test preparing a new GST return."""
        mock_gst_engine.prepare_f5.return_value = {
            'box_1': Decimal('10000.00'),
            'box_2': Decimal('5000.00'),
            'box_3': Decimal('1000.00'),
            'box_5': Decimal('8000.00'),
            'box_6': Decimal('900.00'),
            'box_7': Decimal('720.00'),
        }
        
        company = CompanyFactory()
        user = UserFactory()
        
        gst_return = GSTReturnService.prepare_return(
            company=company,
            quarter=1,
            year=2024,
            prepared_by=user,
        )
        
        assert gst_return.id is not None
        assert gst_return.quarter == 1
        assert gst_return.year == 2024
        assert gst_return.box_1 == Decimal('10000.00')
        assert gst_return.prepared_by == user
    
    @patch('apps.compliance.services.gst_return_service.GSTEngine')
    def test_prepare_return_computes_boxes(self, mock_gst_engine):
        """Test that prepare_return computes derived boxes."""
        mock_gst_engine.prepare_f5.return_value = {
            'box_1': Decimal('10000.00'),
            'box_2': Decimal('5000.00'),
            'box_3': Decimal('1000.00'),
            'box_5': Decimal('8000.00'),
            'box_6': Decimal('900.00'),
            'box_7': Decimal('720.00'),
        }
        
        company = CompanyFactory()
        
        gst_return = GSTReturnService.prepare_return(
            company=company,
            quarter=2,
            year=2024,
        )
        
        # Box 4 = 1+2+3 = 16000
        assert gst_return.box_4 == Decimal('16000.00')
        # Box 8 = 6-7 = 180
        assert gst_return.box_8 == Decimal('180.00')
    
    def test_prepare_return_rejects_duplicate(self):
        """Test that existing submitted returns cannot be overwritten."""
        gst_return = GSTReturnFactory(status='submitted')
        
        with pytest.raises(ValueError, match="already exists"):
            GSTReturnService.prepare_return(
                company=gst_return.company,
                quarter=gst_return.quarter,
                year=gst_return.year,
            )


@pytest.mark.django_db
class TestGSTReturnServiceValidate:
    """Tests for GSTReturnService.validate_return."""
    
    def test_validate_return_success(self):
        """Test validating a correct return."""
        gst_return = GSTReturnFactory()
        
        is_valid, errors = GSTReturnService.validate_return(gst_return)
        
        assert is_valid is True
        assert len(errors) == 0
        
        gst_return.refresh_from_db()
        assert gst_return.status == 'validated'
    
    def test_validate_return_invalid_boxes(self):
        """Test validation fails with incorrect boxes."""
        gst_return = GSTReturnFactory(
            box_4=Decimal('0.00'),  # Wrong
        )
        
        is_valid, errors = GSTReturnService.validate_return(gst_return)
        
        assert is_valid is False
        assert len(errors) > 0


@pytest.mark.django_db
class TestGSTReturnServiceSubmit:
    """Tests for GSTReturnService.submit_return."""
    
    def test_submit_return_success(self):
        """Test submitting a validated return."""
        gst_return = ValidatedGSTReturnFactory()
        user = UserFactory()
        
        result = GSTReturnService.submit_return(
            gst_return=gst_return,
            submitted_by=user,
            iras_reference='IR-2024-001',
        )
        
        assert result.status == 'submitted'
        assert result.submitted_by == user
        assert result.iras_reference == 'IR-2024-001'
    
    def test_submit_return_fails_if_not_validated(self):
        """Test that draft returns cannot be submitted."""
        gst_return = GSTReturnFactory(status='draft')
        user = UserFactory()
        
        with pytest.raises(ValueError, match="validated"):
            GSTReturnService.submit_return(
                gst_return=gst_return,
                submitted_by=user,
            )
