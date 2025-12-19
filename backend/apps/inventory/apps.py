"""
Django app configuration for inventory domain.
"""
from django.apps import AppConfig


class InventoryConfig(AppConfig):
    """Configuration for the inventory application."""
    
    name = 'apps.inventory'
    verbose_name = 'Inventory Management'
    default_auto_field = 'django.db.models.UUIDField'
