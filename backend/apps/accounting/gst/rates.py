"""
Historical GST rates for Singapore.

Rate History:
- April 1, 1994: GST introduced at 3%
- January 1, 2003: Increased to 4%
- January 1, 2004: Increased to 5%
- July 1, 2007: Increased to 7%
- January 1, 2023: Increased to 8%
- January 1, 2024: Increased to 9% (current)
"""
from datetime import date
from decimal import Decimal
from typing import List, Tuple

from django.conf import settings


# GST rate history as (effective_date, rate) tuples
# Sorted by date descending for efficient lookup
GST_RATES: List[Tuple[date, Decimal]] = [
    (date(2024, 1, 1), Decimal('0.09')),   # Current rate
    (date(2023, 1, 1), Decimal('0.08')),   # 2023
    (date(2007, 7, 1), Decimal('0.07')),   # 2007-2022
    (date(2004, 1, 1), Decimal('0.05')),   # 2004-2007
    (date(2003, 1, 1), Decimal('0.04')),   # 2003
    (date(1994, 4, 1), Decimal('0.03')),   # GST introduction
    (date.min, Decimal('0.00')),           # Before GST
]


def get_gst_rate(transaction_date: date) -> Decimal:
    """
    Get the applicable GST rate for a given transaction date.
    
    Uses historical rate lookup for accurate GST calculation
    on historical transactions.
    
    Args:
        transaction_date: Date of the transaction
        
    Returns:
        Decimal GST rate (e.g., 0.09 for 9%)
    """
    for effective_date, rate in GST_RATES:
        if transaction_date >= effective_date:
            return rate
    return Decimal('0.00')


def get_current_gst_rate() -> Decimal:
    """
    Get the current GST rate.
    
    Uses environment variable override if set, otherwise
    uses the most recent rate from GST_RATES.
    
    Returns:
        Current GST rate as Decimal
    """
    # Check for environment override
    env_rate = getattr(settings, 'GST_DEFAULT_RATE', None)
    if env_rate is not None:
        if isinstance(env_rate, Decimal):
            return env_rate
        return Decimal(str(env_rate))
    
    # Return most recent rate
    return GST_RATES[0][1]


def format_gst_rate_percent(rate: Decimal) -> str:
    """
    Format GST rate as percentage string.
    
    Args:
        rate: Decimal rate (e.g., 0.09)
        
    Returns:
        Formatted string (e.g., "9%")
    """
    percent = rate * 100
    if percent == int(percent):
        return f"{int(percent)}%"
    return f"{percent}%"
