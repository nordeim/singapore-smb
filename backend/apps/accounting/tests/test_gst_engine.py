"""
Tests for GST engine.
"""
import pytest
from decimal import Decimal
from datetime import date

from apps.accounting.gst import GSTEngine, get_gst_rate, get_current_gst_rate
from apps.accounting.gst.engine import GSTCalculationResult, F5Return


pytestmark = pytest.mark.django_db


class TestGSTRates:
    """Tests for GST rate lookup."""
    
    def test_current_rate(self):
        """Test current rate is 9%."""
        rate = get_current_gst_rate()
        assert rate == Decimal('0.09')
    
    def test_rate_2024(self):
        """Test 2024 rate is 9%."""
        rate = get_gst_rate(date(2024, 6, 15))
        assert rate == Decimal('0.09')
    
    def test_rate_2023(self):
        """Test 2023 rate is 8%."""
        rate = get_gst_rate(date(2023, 6, 15))
        assert rate == Decimal('0.08')
    
    def test_rate_2022(self):
        """Test 2022 rate is 7%."""
        rate = get_gst_rate(date(2022, 6, 15))
        assert rate == Decimal('0.07')
    
    def test_rate_2006(self):
        """Test 2006 rate is 5%."""
        rate = get_gst_rate(date(2006, 6, 15))
        assert rate == Decimal('0.05')
    
    def test_rate_before_gst(self):
        """Test rate before GST introduction is 0%."""
        rate = get_gst_rate(date(1990, 1, 1))
        assert rate == Decimal('0.00')


class TestGSTEngineCalculation:
    """Tests for GSTEngine.calculate()."""
    
    def test_calculate_sr_9_percent(self):
        """Test standard rated calculation at 9%."""
        result = GSTEngine.calculate(
            amount=Decimal('100.00'),
            gst_code='SR',
            transaction_date=date(2024, 6, 15)
        )
        
        assert result.net_amount == Decimal('100.00')
        assert result.gst_amount == Decimal('9.00')
        assert result.gross_amount == Decimal('109.00')
        assert result.gst_rate == Decimal('0.09')
    
    def test_calculate_sr_8_percent(self):
        """Test standard rated calculation at 8% (2023)."""
        result = GSTEngine.calculate(
            amount=Decimal('100.00'),
            gst_code='SR',
            transaction_date=date(2023, 6, 15)
        )
        
        assert result.net_amount == Decimal('100.00')
        assert result.gst_amount == Decimal('8.00')
        assert result.gross_amount == Decimal('108.00')
        assert result.gst_rate == Decimal('0.08')
    
    def test_calculate_zr_zero_percent(self):
        """Test zero rated calculation."""
        result = GSTEngine.calculate(
            amount=Decimal('100.00'),
            gst_code='ZR',
        )
        
        assert result.net_amount == Decimal('100.00')
        assert result.gst_amount == Decimal('0.00')
        assert result.gross_amount == Decimal('100.00')
        assert result.gst_rate == Decimal('0.00')
    
    def test_calculate_es_exempt(self):
        """Test exempt supply calculation."""
        result = GSTEngine.calculate(
            amount=Decimal('100.00'),
            gst_code='ES',
        )
        
        assert result.gst_amount == Decimal('0.00')
        assert result.gross_amount == Decimal('100.00')
    
    def test_calculate_os_out_of_scope(self):
        """Test out of scope calculation."""
        result = GSTEngine.calculate(
            amount=Decimal('100.00'),
            gst_code='OS',
        )
        
        assert result.gst_amount == Decimal('0.00')
        assert result.gross_amount == Decimal('100.00')
    
    def test_calculate_gst_inclusive(self):
        """Test GST-inclusive calculation."""
        result = GSTEngine.calculate(
            amount=Decimal('109.00'),
            gst_code='SR',
            amount_includes_gst=True,
        )
        
        assert result.net_amount == Decimal('100.00')
        assert result.gst_amount == Decimal('9.00')
        assert result.gross_amount == Decimal('109.00')
    
    def test_calculate_rounding(self):
        """Test GST rounding (ROUND_HALF_UP)."""
        result = GSTEngine.calculate(
            amount=Decimal('33.33'),
            gst_code='SR',
            transaction_date=date(2024, 1, 1)
        )
        
        # 33.33 * 0.09 = 2.9997 -> rounds to 3.00
        assert result.gst_amount == Decimal('3.00')
        assert result.gross_amount == Decimal('36.33')


class TestGSTEngineRateLookup:
    """Tests for GSTEngine.get_rate()."""
    
    def test_get_rate_sr_current(self):
        """Test SR rate is current GST rate."""
        rate = GSTEngine.get_rate('SR')
        assert rate == Decimal('0.09')
    
    def test_get_rate_sr_historical(self):
        """Test SR rate for historical date."""
        rate = GSTEngine.get_rate('SR', date(2020, 1, 1))
        assert rate == Decimal('0.07')
    
    def test_get_rate_zr_always_zero(self):
        """Test ZR rate is always 0."""
        rate = GSTEngine.get_rate('ZR', date(2024, 1, 1))
        assert rate == Decimal('0.00')
    
    def test_get_rate_es_always_zero(self):
        """Test ES rate is always 0."""
        rate = GSTEngine.get_rate('ES', date(2024, 1, 1))
        assert rate == Decimal('0.00')
    
    def test_get_rate_os_always_zero(self):
        """Test OS rate is always 0."""
        rate = GSTEngine.get_rate('OS', date(2024, 1, 1))
        assert rate == Decimal('0.00')
    
    def test_get_rate_unknown_code(self):
        """Test unknown code returns 0."""
        rate = GSTEngine.get_rate('XX', date(2024, 1, 1))
        assert rate == Decimal('0.00')


class TestF5Return:
    """Tests for F5 return validation."""
    
    def test_validate_f5_valid(self):
        """Test valid F5 return passes validation."""
        f5 = F5Return(
            company_id='test-company-id',
            year=2024,
            quarter=1,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 3, 31),
            box_1=Decimal('10000.00'),  # Standard rated
            box_2=Decimal('2000.00'),   # Zero rated
            box_3=Decimal('500.00'),    # Exempt
            box_4=Decimal('12500.00'),  # Total (1+2+3)
            box_5=Decimal('5000.00'),   # Purchases
            box_6=Decimal('900.00'),    # Output tax (10000 * 0.09)
            box_7=Decimal('450.00'),    # Input tax
            box_8=Decimal('450.00'),    # Net (6-7)
        )
        
        is_valid, errors = GSTEngine.validate_f5(f5)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_f5_invalid_box_4(self):
        """Test invalid Box 4 total fails validation."""
        f5 = F5Return(
            company_id='test-company-id',
            year=2024,
            quarter=1,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 3, 31),
            box_1=Decimal('10000.00'),
            box_2=Decimal('2000.00'),
            box_3=Decimal('500.00'),
            box_4=Decimal('10000.00'),  # Wrong! Should be 12500
            box_5=Decimal('5000.00'),
            box_6=Decimal('900.00'),
            box_7=Decimal('450.00'),
            box_8=Decimal('450.00'),
        )
        
        is_valid, errors = GSTEngine.validate_f5(f5)
        assert is_valid is False
        assert any('Box 4' in e for e in errors)
    
    def test_validate_f5_invalid_box_8(self):
        """Test invalid Box 8 net fails validation."""
        f5 = F5Return(
            company_id='test-company-id',
            year=2024,
            quarter=1,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 3, 31),
            box_1=Decimal('10000.00'),
            box_2=Decimal('2000.00'),
            box_3=Decimal('500.00'),
            box_4=Decimal('12500.00'),
            box_5=Decimal('5000.00'),
            box_6=Decimal('900.00'),
            box_7=Decimal('450.00'),
            box_8=Decimal('500.00'),  # Wrong! Should be 450
        )
        
        is_valid, errors = GSTEngine.validate_f5(f5)
        assert is_valid is False
        assert any('Box 8' in e for e in errors)
    
    def test_validate_f5_negative_box(self):
        """Test negative box value fails validation."""
        f5 = F5Return(
            company_id='test-company-id',
            year=2024,
            quarter=1,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 3, 31),
            box_1=Decimal('-100.00'),  # Negative!
            box_2=Decimal('0.00'),
            box_3=Decimal('0.00'),
            box_4=Decimal('-100.00'),
            box_5=Decimal('0.00'),
            box_6=Decimal('-9.00'),
            box_7=Decimal('0.00'),
            box_8=Decimal('-9.00'),
        )
        
        is_valid, errors = GSTEngine.validate_f5(f5)
        assert is_valid is False
        assert any('negative' in e.lower() for e in errors)
    
    def test_f5_refund_scenario(self):
        """Test F5 with refund (Box 8 negative) is valid."""
        f5 = F5Return(
            company_id='test-company-id',
            year=2024,
            quarter=1,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 3, 31),
            box_1=Decimal('1000.00'),
            box_2=Decimal('0.00'),
            box_3=Decimal('0.00'),
            box_4=Decimal('1000.00'),
            box_5=Decimal('10000.00'),  # Large purchases
            box_6=Decimal('90.00'),     # Output tax
            box_7=Decimal('900.00'),    # Input tax (larger)
            box_8=Decimal('-810.00'),   # Net is negative (refund)
        )
        
        is_valid, errors = GSTEngine.validate_f5(f5)
        assert is_valid is True  # Box 8 can be negative
