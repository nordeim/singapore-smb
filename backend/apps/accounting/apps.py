"""
Django app configuration for accounting module.
"""
from django.apps import AppConfig


class AccountingConfig(AppConfig):
    """Configuration for the Accounting application."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounting'
    verbose_name = 'Accounting'
    
    def ready(self):
        """Import signals when app is ready."""
        pass  # Signals will be added as needed
