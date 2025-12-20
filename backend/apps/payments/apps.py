"""
Django app configuration for payments module.

Provides:
- Payment gateway abstraction
- Stripe integration
- HitPay integration (PayNow, GrabPay)
- Webhook handling
"""
from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    """Configuration for the payments app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.payments'
    verbose_name = 'Payments'
