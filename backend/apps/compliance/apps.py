"""
Django app configuration for compliance module.

Provides:
- GST F5 return management
- PDPA consent tracking
- Data access request handling
- Audit logging
"""
from django.apps import AppConfig


class ComplianceConfig(AppConfig):
    """Configuration for the compliance app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.compliance'
    verbose_name = 'Compliance'
    
    def ready(self):
        """Import signals when app is ready."""
        try:
            import apps.compliance.signals  # noqa: F401
        except ImportError:
            pass
