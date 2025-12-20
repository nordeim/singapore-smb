"""
Compliance signals for automatic audit logging.

Automatically creates audit log entries when configured models change.
"""
import logging
from typing import Optional

from django.conf import settings
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db import models

from apps.compliance.models import AuditLog
from apps.compliance.services import AuditService


logger = logging.getLogger(__name__)


# Store pre-save state for diff calculation
_pre_save_state = {}


def get_audit_models():
    """Get list of models to audit from settings."""
    return getattr(settings, 'AUDIT_MODELS', [])


def _get_model_key(instance) -> str:
    """Get unique key for model instance."""
    return f"{instance._meta.app_label}.{instance._meta.model_name}:{instance.pk}"


def _should_audit(instance) -> bool:
    """Check if this model instance should be audited."""
    model_path = f"{instance._meta.app_label}.{instance._meta.model_name}"
    audit_models = get_audit_models()
    
    # Check direct match
    if model_path in [m.lower() for m in audit_models]:
        return True
    
    # Check with app.Model format
    for audit_model in audit_models:
        if audit_model.lower() == model_path:
            return True
    
    return False


@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    """
    Store pre-save state for update diff calculation.
    """
    # Skip audit logs themselves
    if isinstance(instance, AuditLog):
        return
    
    if not _should_audit(instance):
        return
    
    # Only for existing instances (updates)
    if instance.pk:
        try:
            # Get current DB values
            current = sender.objects.filter(pk=instance.pk).values().first()
            if current:
                key = _get_model_key(instance)
                _pre_save_state[key] = dict(current)
        except Exception as e:
            logger.debug(f"Could not capture pre-save state: {e}")


@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    """
    Create audit log entry after model save.
    """
    # Skip audit logs themselves
    if isinstance(instance, AuditLog):
        return
    
    if not _should_audit(instance):
        return
    
    try:
        if created:
            # CREATE action
            AuditService.log_model_create(instance)
        else:
            # UPDATE action
            key = _get_model_key(instance)
            old_data = _pre_save_state.pop(key, {})
            AuditService.log_model_update(instance, old_data)
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")


@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    """
    Create audit log entry after model delete.
    """
    # Skip audit logs themselves
    if isinstance(instance, AuditLog):
        return
    
    if not _should_audit(instance):
        return
    
    try:
        AuditService.log_model_delete(instance)
    except Exception as e:
        logger.error(f"Failed to create audit log for delete: {e}")
