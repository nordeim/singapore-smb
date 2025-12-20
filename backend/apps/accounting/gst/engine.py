"""
GST Engine for Singapore GST calculations and F5 return preparation.

Provides:
- GST calculation for different tax codes (SR, ZR, ES, OS)
- Historical rate lookup
- F5 return preparation with box calculations
- F5 validation
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Dict, Any, Tuple, List
import logging

from django.db.models import Sum, Q
from django.utils import timezone

from apps.accounting.gst.rates import get_gst_rate, get_current_gst_rate


logger = logging.getLogger(__name__)


@dataclass
class GSTCalculationResult:
    """Result of GST calculation."""
    net_amount: Decimal
    gst_amount: Decimal
    gross_amount: Decimal
    gst_rate: Decimal
    gst_code: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'net_amount': str(self.net_amount),
            'gst_amount': str(self.gst_amount),
            'gross_amount': str(self.gross_amount),
            'gst_rate': str(self.gst_rate),
            'gst_code': self.gst_code,
        }


@dataclass
class F5Return:
    """GST F5 Return data structure."""
    company_id: str
    year: int
    quarter: int
    period_start: date
    period_end: date
    
    # Box values
    box_1: Decimal  # Standard-rated supplies
    box_2: Decimal  # Zero-rated supplies
    box_3: Decimal  # Exempt supplies
    box_4: Decimal  # Total supplies (1+2+3)
    box_5: Decimal  # Total taxable purchases
    box_6: Decimal  # Output tax due
    box_7: Decimal  # Input tax claimable
    box_8: Decimal  # Net GST payable (6-7)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'company_id': self.company_id,
            'year': self.year,
            'quarter': self.quarter,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'box_1': str(self.box_1),
            'box_2': str(self.box_2),
            'box_3': str(self.box_3),
            'box_4': str(self.box_4),
            'box_5': str(self.box_5),
            'box_6': str(self.box_6),
            'box_7': str(self.box_7),
            'box_8': str(self.box_8),
        }


class GSTEngine:
    """
    GST calculation engine for Singapore.
    
    Handles:
    - GST calculation for transactions
    - Historical rate lookup
    - F5 return preparation
    """
    
    # GST code to treatment mapping
    GST_CODES = {
        'SR': 'Standard Rated',      # Subject to GST at standard rate
        'ZR': 'Zero Rated',          # 0% rate (exports, international services)
        'ES': 'Exempt Supply',       # Not subject to GST
        'OS': 'Out of Scope',        # Outside GST regime
    }
    
    @classmethod
    def calculate(
        cls,
        amount: Decimal,
        gst_code: str,
        transaction_date: Optional[date] = None,
        amount_includes_gst: bool = False,
    ) -> GSTCalculationResult:
        """
        Calculate GST for a transaction.
        
        Args:
            amount: Transaction amount
            gst_code: GST treatment code (SR, ZR, ES, OS)
            transaction_date: Date for rate lookup (default: today)
            amount_includes_gst: If True, amount is GST-inclusive
            
        Returns:
            GSTCalculationResult with net, GST, and gross amounts
        """
        # Get applicable rate
        rate = cls.get_rate(gst_code, transaction_date)
        
        if amount_includes_gst and rate > 0:
            # Extract GST from inclusive amount
            net_amount = (amount / (1 + rate)).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            gst_amount = amount - net_amount
            gross_amount = amount
        else:
            # Calculate GST on exclusive amount
            net_amount = amount
            gst_amount = (amount * rate).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            gross_amount = net_amount + gst_amount
        
        return GSTCalculationResult(
            net_amount=net_amount,
            gst_amount=gst_amount,
            gross_amount=gross_amount,
            gst_rate=rate,
            gst_code=gst_code,
        )
    
    @classmethod
    def get_rate(
        cls,
        gst_code: str,
        transaction_date: Optional[date] = None,
    ) -> Decimal:
        """
        Get GST rate for a given code and date.
        
        Args:
            gst_code: GST treatment code
            transaction_date: Date for rate lookup
            
        Returns:
            Decimal rate (e.g., 0.09 for 9%)
        """
        # Non-taxable codes always return 0
        if gst_code in ('ZR', 'ES', 'OS'):
            return Decimal('0.00')
        
        # Standard Rated uses historical rate
        if gst_code == 'SR':
            if transaction_date:
                return get_gst_rate(transaction_date)
            return get_current_gst_rate()
        
        # Unknown code defaults to 0
        logger.warning(f"Unknown GST code: {gst_code}")
        return Decimal('0.00')
    
    @classmethod
    def prepare_f5(
        cls,
        company,
        quarter: int,
        year: int,
    ) -> F5Return:
        """
        Prepare GST F5 return data for a quarter.
        
        Aggregates orders and invoices by GST code to calculate
        F5 box values.
        
        Args:
            company: Company model instance
            quarter: Quarter (1-4)
            year: Year
            
        Returns:
            F5Return with all box values calculated
        """
        from apps.commerce.models import Order
        
        # Calculate quarter date range
        period_start, period_end = cls._get_quarter_dates(quarter, year)
        
        # Initialize box values
        box_1 = Decimal('0.00')  # Standard-rated supplies
        box_2 = Decimal('0.00')  # Zero-rated supplies
        box_3 = Decimal('0.00')  # Exempt supplies
        box_5 = Decimal('0.00')  # Taxable purchases (TODO: from expenses)
        box_6 = Decimal('0.00')  # Output tax
        box_7 = Decimal('0.00')  # Input tax (TODO: from expenses)
        
        # Query orders in the period
        orders = Order.objects.filter(
            company=company,
            created_at__date__gte=period_start,
            created_at__date__lte=period_end,
            status__in=['confirmed', 'processing', 'shipped', 'delivered'],
        )
        
        # Aggregate by GST code from order items
        # For simplicity, we use order-level F5 fields if available
        order_aggregates = orders.aggregate(
            total_sr=Sum('gst_box_1_amount'),
            total_gst=Sum('gst_box_6_amount'),
        )
        
        box_1 = order_aggregates['total_sr'] or Decimal('0.00')
        box_6 = order_aggregates['total_gst'] or Decimal('0.00')
        
        # If order doesn't have F5 fields, calculate from items
        if box_1 == Decimal('0.00') and box_6 == Decimal('0.00'):
            for order in orders:
                for item in order.items.select_related('product'):
                    product_gst_code = item.product.gst_code if item.product else 'SR'
                    item_total = item.unit_price * item.quantity
                    
                    if product_gst_code == 'SR':
                        box_1 += item_total
                        gst_result = cls.calculate(item_total, 'SR', order.created_at.date())
                        box_6 += gst_result.gst_amount
                    elif product_gst_code == 'ZR':
                        box_2 += item_total
                    elif product_gst_code == 'ES':
                        box_3 += item_total
                    # OS is out of scope, not included
        
        # Calculate derived boxes
        box_4 = box_1 + box_2 + box_3  # Total supplies
        box_8 = box_6 - box_7          # Net GST payable
        
        return F5Return(
            company_id=str(company.id),
            year=year,
            quarter=quarter,
            period_start=period_start,
            period_end=period_end,
            box_1=box_1,
            box_2=box_2,
            box_3=box_3,
            box_4=box_4,
            box_5=box_5,
            box_6=box_6,
            box_7=box_7,
            box_8=box_8,
        )
    
    @classmethod
    def validate_f5(cls, f5_return: F5Return) -> Tuple[bool, List[str]]:
        """
        Validate F5 return data.
        
        Checks:
        - Box 4 = Box 1 + Box 2 + Box 3
        - Box 8 = Box 6 - Box 7
        - All values are non-negative (except Box 8)
        
        Args:
            f5_return: F5Return to validate
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        # Check Box 4 total
        expected_box_4 = f5_return.box_1 + f5_return.box_2 + f5_return.box_3
        if f5_return.box_4 != expected_box_4:
            errors.append(
                f"Box 4 ({f5_return.box_4}) should equal "
                f"Box 1 + Box 2 + Box 3 ({expected_box_4})"
            )
        
        # Check Box 8 net
        expected_box_8 = f5_return.box_6 - f5_return.box_7
        if f5_return.box_8 != expected_box_8:
            errors.append(
                f"Box 8 ({f5_return.box_8}) should equal "
                f"Box 6 - Box 7 ({expected_box_8})"
            )
        
        # Check non-negative values (except Box 8 which can be negative for refund)
        for box_name, value in [
            ('Box 1', f5_return.box_1),
            ('Box 2', f5_return.box_2),
            ('Box 3', f5_return.box_3),
            ('Box 4', f5_return.box_4),
            ('Box 5', f5_return.box_5),
            ('Box 6', f5_return.box_6),
            ('Box 7', f5_return.box_7),
        ]:
            if value < 0:
                errors.append(f"{box_name} cannot be negative: {value}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _get_quarter_dates(quarter: int, year: int) -> Tuple[date, date]:
        """Get start and end dates for a quarter."""
        quarter_starts = {
            1: (1, 1),   # Jan 1
            2: (4, 1),   # Apr 1
            3: (7, 1),   # Jul 1
            4: (10, 1),  # Oct 1
        }
        quarter_ends = {
            1: (3, 31),  # Mar 31
            2: (6, 30),  # Jun 30
            3: (9, 30),  # Sep 30
            4: (12, 31), # Dec 31
        }
        
        start_month, start_day = quarter_starts[quarter]
        end_month, end_day = quarter_ends[quarter]
        
        return (
            date(year, start_month, start_day),
            date(year, end_month, end_day),
        )
