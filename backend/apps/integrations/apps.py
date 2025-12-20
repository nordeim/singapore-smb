"""
Django app configuration for integrations module.

Provides:
- Logistics integrations (NinjaVan, SingPost)
- Shipping rate comparison
- Shipment tracking
"""
from django.apps import AppConfig


class IntegrationsConfig(AppConfig):
    """Configuration for the integrations app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.integrations'
    verbose_name = 'Integrations'
