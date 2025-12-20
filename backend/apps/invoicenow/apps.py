"""
Django app configuration for InvoiceNow module.

Provides:
- PEPPOL BIS Billing 3.0 UBL generation
- XML digital signing
- Access Point submission
"""
from django.apps import AppConfig


class InvoiceNowConfig(AppConfig):
    """Configuration for the InvoiceNow app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.invoicenow'
    verbose_name = 'InvoiceNow (PEPPOL)'
