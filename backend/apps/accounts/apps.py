"""
Django app configuration for accounts module.
"""
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Configuration for the accounts app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'User Accounts'
    
    def ready(self):
        """
        Called when Django starts.
        Import signals to register them.
        """
        try:
            import apps.accounts.signals  # noqa: F401
        except ImportError:
            pass
