"""
Commerce app configuration.
"""
from django.apps import AppConfig


class CommerceConfig(AppConfig):
    """Configuration for the Commerce application."""
    
    name = 'apps.commerce'
    verbose_name = 'Commerce'
    default_auto_field = 'django.db.models.UUIDField'
    
    def ready(self):
        """Import signals when app is ready."""
        pass  # Will add signals in future if needed
