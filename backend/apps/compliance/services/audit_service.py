"""
Audit logging service.

Provides:
- Centralized audit log creation
- Model change tracking
- History retrieval
"""
import logging
from typing import Optional, Any

from django.db.models.signals import post_save, post_delete
from django.db import models

from apps.compliance.models import AuditLog


logger = logging.getLogger(__name__)


class AuditService:
    """
    Service for audit logging operations.
    
    Provides centralized logging of model changes with:
    - Automatic diff calculation
    - User and IP tracking
    - History retrieval by resource
    """
    
    # Fields to exclude from audit logs (sensitive or noise)
    EXCLUDED_FIELDS = {
        'password', 'password_hash', 'last_login', 'updated_at',
    }
    
    @staticmethod
    def log_change(
        action: str,
        resource_type: str,
        resource_id,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
        user=None,
        ip_address: str = None,
        company=None,
    ) -> AuditLog:
        """
        Create an audit log entry.
        
        Args:
            action: CREATE, UPDATE, or DELETE
            resource_type: Model name (e.g., 'commerce.order')
            resource_id: Primary key of the resource
            old_values: Previous values (for UPDATE/DELETE)
            new_values: New values (for CREATE/UPDATE)
            user: User who made the change
            ip_address: Request IP address
            company: Company context
            
        Returns:
            Created AuditLog
        """
        audit_log = AuditLog.objects.create(
            company=company,
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values or {},
            new_values=new_values or {},
            ip_address=ip_address,
        )
        
        logger.debug(
            f"Audit log: {action} {resource_type} {resource_id}"
        )
        
        return audit_log
    
    @staticmethod
    def log_model_create(
        instance,
        user=None,
        ip_address: str = None,
    ) -> AuditLog:
        """
        Log a model creation.
        
        Args:
            instance: The created model instance
            user: User who created it
            ip_address: Request IP
            
        Returns:
            Created AuditLog
        """
        new_values = AuditService._serialize_instance(instance)
        company = AuditService._get_company(instance)
        
        return AuditLog.objects.create_for_model(
            action='CREATE',
            instance=instance,
            new_values=new_values,
            user=user,
            ip_address=ip_address,
            company=company,
        )
    
    @staticmethod
    def log_model_update(
        instance,
        old_data: dict,
        user=None,
        ip_address: str = None,
    ) -> Optional[AuditLog]:
        """
        Log a model update with diff.
        
        Args:
            instance: The updated model instance
            old_data: Previous field values
            user: User who updated it
            ip_address: Request IP
            
        Returns:
            Created AuditLog or None if no changes
        """
        new_values = AuditService._serialize_instance(instance)
        
        # Calculate diff
        old_values = {}
        new_diff = {}
        for field, new_val in new_values.items():
            old_val = old_data.get(field)
            if old_val != new_val:
                old_values[field] = old_val
                new_diff[field] = new_val
        
        if not old_values:
            return None  # No actual changes
        
        company = AuditService._get_company(instance)
        
        return AuditLog.objects.create_for_model(
            action='UPDATE',
            instance=instance,
            old_values=old_values,
            new_values=new_diff,
            user=user,
            ip_address=ip_address,
            company=company,
        )
    
    @staticmethod
    def log_model_delete(
        instance,
        user=None,
        ip_address: str = None,
    ) -> AuditLog:
        """
        Log a model deletion.
        
        Args:
            instance: The deleted model instance
            user: User who deleted it
            ip_address: Request IP
            
        Returns:
            Created AuditLog
        """
        old_values = AuditService._serialize_instance(instance)
        company = AuditService._get_company(instance)
        
        return AuditLog.objects.create_for_model(
            action='DELETE',
            instance=instance,
            old_values=old_values,
            user=user,
            ip_address=ip_address,
            company=company,
        )
    
    @staticmethod
    def get_history(resource_type: str, resource_id) -> list:
        """
        Get audit history for a specific resource.
        
        Args:
            resource_type: Model name
            resource_id: Primary key
            
        Returns:
            List of AuditLog records ordered by time
        """
        return list(AuditLog.objects.filter(
            resource_type=resource_type,
            resource_id=resource_id,
        ).order_by('-created_at'))
    
    @staticmethod
    def get_user_activity(user_id, since=None, limit: int = 100) -> list:
        """
        Get recent activity by a user.
        
        Args:
            user_id: User primary key
            since: Optional datetime to filter from
            limit: Maximum records to return
            
        Returns:
            List of AuditLog records
        """
        queryset = AuditLog.objects.filter(user_id=user_id)
        
        if since:
            queryset = queryset.filter(created_at__gte=since)
        
        return list(queryset.order_by('-created_at')[:limit])
    
    @staticmethod
    def _serialize_instance(instance) -> dict:
        """
        Serialize model instance to dict for audit logging.
        
        Args:
            instance: Model instance
            
        Returns:
            Dict of field values
        """
        data = {}
        
        for field in instance._meta.get_fields():
            # Skip excluded and complex fields
            if field.name in AuditService.EXCLUDED_FIELDS:
                continue
            if field.is_relation and not field.many_to_one:
                continue
            
            try:
                value = getattr(instance, field.name, None)
                
                # Handle foreign keys
                if field.many_to_one and value is not None:
                    value = str(value.pk) if hasattr(value, 'pk') else str(value)
                
                # Convert to JSON-serializable
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                elif hasattr(value, '__str__') and not isinstance(value, (str, int, float, bool, type(None))):
                    value = str(value)
                
                data[field.name] = value
            except AttributeError:
                continue
        
        return data
    
    @staticmethod
    def _get_company(instance):
        """Get company from instance if available."""
        if hasattr(instance, 'company'):
            return instance.company
        elif hasattr(instance, 'company_id'):
            from apps.accounts.models import Company
            try:
                return Company.objects.get(pk=instance.company_id)
            except Company.DoesNotExist:
                return None
        return None
