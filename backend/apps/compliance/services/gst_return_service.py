"""
GST Return service for F5 preparation and submission.

Provides:
- GST F5 return preparation from order data
- Return validation
- Submission workflow
"""
import logging
from decimal import Decimal
from datetime import date
from typing import Optional, Tuple, List

from django.db import transaction
from django.db.models import Sum, Q

from apps.compliance.models import GSTReturn
from apps.accounting.gst import GSTEngine


logger = logging.getLogger(__name__)


class GSTReturnService:
    """
    Service for GST F5 return management.
    
    Integrates with the accounting GST Engine to:
    - Prepare returns from order data
    - Validate box calculations
    - Manage submission workflow
    """
    
    @staticmethod
    def prepare_return(
        company,
        quarter: int,
        year: int,
        prepared_by=None,
    ) -> GSTReturn:
        """
        Prepare a GST F5 return for a quarter.
        
        Calculates all box values from order and invoice data.
        
        Args:
            company: Company to prepare return for
            quarter: Quarter (1-4)
            year: Year
            prepared_by: User preparing the return
            
        Returns:
            Created GSTReturn with populated boxes
        """
        # Calculate period dates
        period_start, period_end = GSTReturnService._get_quarter_dates(quarter, year)
        
        # Check for existing return
        existing = GSTReturn.objects.filter(
            company=company,
            year=year,
            quarter=quarter,
        ).first()
        
        if existing and existing.status not in ['draft', 'rejected']:
            raise ValueError(
                f"Return for Q{quarter}/{year} already exists with status {existing.status}"
            )
        
        # Use GST Engine to prepare F5 data
        f5_data = GSTEngine.prepare_f5(company.id, quarter, year)
        
        with transaction.atomic():
            if existing:
                gst_return = existing
            else:
                gst_return = GSTReturn(
                    company=company,
                    quarter=quarter,
                    year=year,
                )
            
            # Set period
            gst_return.period_start = period_start
            gst_return.period_end = period_end
            
            # Set box values from F5 data
            gst_return.box_1 = f5_data.get('box_1', Decimal('0.00'))
            gst_return.box_2 = f5_data.get('box_2', Decimal('0.00'))
            gst_return.box_3 = f5_data.get('box_3', Decimal('0.00'))
            gst_return.box_5 = f5_data.get('box_5', Decimal('0.00'))
            gst_return.box_6 = f5_data.get('box_6', Decimal('0.00'))
            gst_return.box_7 = f5_data.get('box_7', Decimal('0.00'))
            
            # Compute derived boxes
            gst_return.compute_boxes()
            
            gst_return.prepared_by = prepared_by
            gst_return.status = 'draft'
            gst_return.save()
            
            logger.info(
                f"Prepared GST return Q{quarter}/{year} for company {company.id}"
            )
            
            return gst_return
    
    @staticmethod
    def validate_return(gst_return: GSTReturn) -> Tuple[bool, List[str]]:
        """
        Validate a GST return.
        
        Checks:
        - Box calculations are correct
        - Required fields are populated
        - Business rules are satisfied
        
        Args:
            gst_return: Return to validate
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        # Check box calculations
        is_valid, box_errors = gst_return.validate_boxes()
        errors.extend(box_errors)
        
        # Check period is set
        if not gst_return.period_start or not gst_return.period_end:
            errors.append("Period start and end dates are required")
        
        # Check period is valid
        if gst_return.period_start and gst_return.period_end:
            if gst_return.period_start > gst_return.period_end:
                errors.append("Period start cannot be after period end")
        
        # Check status allows validation
        if gst_return.status not in ['draft', 'rejected']:
            errors.append(f"Cannot validate return in {gst_return.status} status")
        
        if not errors and gst_return.status == 'draft':
            gst_return.mark_validated()
        
        return (len(errors) == 0, errors)
    
    @staticmethod
    def submit_return(
        gst_return: GSTReturn,
        submitted_by,
        iras_reference: str = '',
    ) -> GSTReturn:
        """
        Submit a GST return.
        
        Args:
            gst_return: Return to submit
            submitted_by: User submitting
            iras_reference: IRAS submission reference
            
        Returns:
            Updated GSTReturn
        """
        if not gst_return.can_submit():
            raise ValueError(
                "Return must be validated before submission"
            )
        
        gst_return.mark_submitted(
            submitted_by=submitted_by,
            iras_reference=iras_reference,
        )
        
        logger.info(
            f"Submitted GST return Q{gst_return.quarter}/{gst_return.year} "
            f"for company {gst_return.company_id}"
        )
        
        return gst_return
    
    @staticmethod
    def get_quarterly_returns(company, year: int) -> List[GSTReturn]:
        """
        Get all GST returns for a year.
        
        Args:
            company: Company to query
            year: Year to query
            
        Returns:
            List of GSTReturn objects
        """
        return list(GSTReturn.objects.filter(
            company=company,
            year=year,
        ).order_by('quarter'))
    
    @staticmethod
    def get_return_summary(company) -> dict:
        """
        Get summary of GST returns for a company.
        
        Returns:
            Dict with current year returns and filing status
        """
        current_year = date.today().year
        current_quarter = (date.today().month - 1) // 3 + 1
        
        returns = GSTReturn.objects.filter(
            company=company,
            year__gte=current_year - 1,
        ).order_by('-year', '-quarter')
        
        summary = {
            'current_year': current_year,
            'current_quarter': current_quarter,
            'returns': [],
            'pending_filing': False,
            'overdue_filing': False,
        }
        
        for gst_return in returns:
            summary['returns'].append({
                'quarter': gst_return.quarter,
                'year': gst_return.year,
                'status': gst_return.status,
                'net_gst': str(gst_return.box_8),
            })
        
        # Check if current quarter needs filing
        current_return = GSTReturn.objects.filter(
            company=company,
            year=current_year,
            quarter=current_quarter,
        ).first()
        
        if not current_return or current_return.status == 'draft':
            summary['pending_filing'] = True
        
        return summary
    
    @staticmethod
    def _get_quarter_dates(quarter: int, year: int) -> Tuple[date, date]:
        """
        Get start and end dates for a quarter.
        
        Args:
            quarter: Quarter number (1-4)
            year: Year
            
        Returns:
            Tuple of (start_date, end_date)
        """
        quarter_months = {
            1: (1, 3),
            2: (4, 6),
            3: (7, 9),
            4: (10, 12),
        }
        
        start_month, end_month = quarter_months[quarter]
        
        start_date = date(year, start_month, 1)
        
        # Calculate end of quarter
        if end_month == 12:
            end_date = date(year, 12, 31)
        else:
            # Last day of end_month
            import calendar
            _, last_day = calendar.monthrange(year, end_month)
            end_date = date(year, end_month, last_day)
        
        return start_date, end_date
