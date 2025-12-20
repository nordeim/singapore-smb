"""
Audit Log model for change tracking.

Matches schema: compliance.audit_logs
Provides immutable audit trail for tracked models.
"""
import uuid
import json
from typing import Any, Optional

from django.db import models
from django.utils import timezone


class AuditLogManager(models.Manager):
    """Custom manager with audit log creation helpers."""
    
    def create_for_model(
        self,
        action: str,
        instance,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
        user=None,
        ip_address: str = None,
        company=None,
    ) -> 'AuditLog':
        """
        Create audit log for a model instance change.
        
        Args:
            action: CREATE, UPDATE, or DELETE
            instance: The model instance that changed
            old_values: Previous field values (for UPDATE/DELETE)
            new_values: New field values (for CREATE/UPDATE)
            user: User who made the change
            ip_address: Request IP address
            company: Company context (if not on instance)
            
        Returns:
            Created AuditLog record
        """
        # Try to get company from instance
        if company is None and hasattr(instance, 'company'):
            company = instance.company
        elif company is None and hasattr(instance, 'company_id'):
            company = getattr(instance, 'company', None)
        
        # Get resource type from model
        resource_type = f"{instance._meta.app_label}.{instance._meta.model_name}"
        
        return self.create(
            company=company,
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=instance.pk,
            old_values=old_values or {},
            new_values=new_values or {},
            ip_address=ip_address,
        )


class AuditLog(models.Model):
    """
    Immutable audit trail for model changes.
    
    Records CREATE, UPDATE, and DELETE actions with:
    - Who made the change (user)
    - What was changed (resource_type, resource_id)
    - What the values were (old_values, new_values as JSONB)
    - Context (company, IP address)
    
    This model is IMMUTABLE - records cannot be updated or deleted.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    company = models.ForeignKey(
        'accounts.Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    
    # Action
    action = models.CharField(
        max_length=50,
        help_text='CREATE, UPDATE, or DELETE'
    )
    resource_type = models.CharField(
        max_length=50,
        help_text='Model name (e.g., commerce.order)'
    )
    resource_id = models.UUIDField(
        null=True,
        blank=True,
        help_text='Primary key of the affected resource'
    )
    
    # Values (JSONB)
    old_values = models.JSONField(
        default=dict,
        blank=True,
        help_text='Previous values before change'
    )
    new_values = models.JSONField(
        default=dict,
        blank=True,
        help_text='New values after change'
    )
    
    # Context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Timestamp (immutable)
    created_at = models.DateTimeField(default=timezone.now)
    
    objects = AuditLogManager()
    
    class Meta:
        db_table = '"compliance"."audit_logs"'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['user']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        user_str = self.user.email if self.user else 'System'
        return f"{user_str} {self.action} {self.resource_type}"
    
    def save(self, *args, **kwargs):
        """
        Override save to enforce immutability.
        
        Audit logs cannot be updated once created.
        """
        if self.pk:
            try:
                existing = AuditLog.objects.get(pk=self.pk)
                if existing:
                    raise ValueError(
                        "AuditLog records are immutable and cannot be updated"
                    )
            except AuditLog.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """
        Override delete to prevent deletion.
        
        Audit logs must be retained for compliance.
        """
        raise ValueError(
            "AuditLog records cannot be deleted for compliance purposes"
        )
    
    @property
    def changes(self) -> dict:
        """
        Get a diff of what changed.
        
        Returns:
            Dict of field names to (old_value, new_value) tuples
        """
        if self.action == 'CREATE':
            return {k: (None, v) for k, v in self.new_values.items()}
        elif self.action == 'DELETE':
            return {k: (v, None) for k, v in self.old_values.items()}
        else:  # UPDATE
            changes = {}
            all_keys = set(self.old_values.keys()) | set(self.new_values.keys())
            for key in all_keys:
                old_val = self.old_values.get(key)
                new_val = self.new_values.get(key)
                if old_val != new_val:
                    changes[key] = (old_val, new_val)
            return changes
    
    @property
    def change_summary(self) -> str:
        """Get a human-readable summary of changes."""
        changes = self.changes
        if not changes:
            return "No changes"
        
        parts = []
        for field, (old, new) in changes.items():
            if self.action == 'CREATE':
                parts.append(f"{field}={new}")
            elif self.action == 'DELETE':
                parts.append(f"{field}={old}")
            else:
                parts.append(f"{field}: {old} → {new}")
        
        return "; ".join(parts[:5])  # Limit to 5 fields
