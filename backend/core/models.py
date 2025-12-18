"""
Core abstract models for Singapore SMB E-commerce Platform.

These base models provide common fields and functionality for all models:
- UUID primary keys for distributed-friendly IDs
- Automatic timestamp tracking
- Audit fields for user tracking
- Soft delete support
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class BaseModel(models.Model):
    """
    Abstract base model with UUID primary key and timestamps.
    
    All models should inherit from this to ensure consistent:
    - UUID-based primary keys (distributed-friendly)
    - Creation and modification timestamps
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier (UUID4)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this record was last updated"
    )
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
    
    def __str__(self):
        return str(self.id)


class AuditableModel(BaseModel):
    """
    Abstract model that tracks which user created/modified records.
    
    Use for models where accountability and audit trails are important.
    Automatically populated via middleware or manual assignment.
    """
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        help_text="User who created this record"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        help_text="User who last modified this record"
    )
    
    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    """
    Manager that excludes soft-deleted records by default.
    
    Use `.all_with_deleted()` to include deleted records.
    """
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)
    
    def all_with_deleted(self):
        """Return all records including soft-deleted ones."""
        return super().get_queryset()
    
    def deleted_only(self):
        """Return only soft-deleted records."""
        return super().get_queryset().filter(deleted_at__isnull=False)


class SoftDeleteModel(BaseModel):
    """
    Abstract model with soft delete functionality.
    
    Instead of permanently deleting records, sets `deleted_at` timestamp.
    PDPA compliance: Allows data retention while marking as "deleted".
    
    Methods:
        delete(): Soft-delete the record
        hard_delete(): Permanently delete the record
        restore(): Restore a soft-deleted record
    """
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When this record was soft-deleted"
    )
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Access all records including deleted
    
    class Meta:
        abstract = True
    
    @property
    def is_deleted(self) -> bool:
        """Check if record is soft-deleted."""
        return self.deleted_at is not None
    
    def delete(self, using=None, keep_parents=False):
        """
        Soft-delete the record by setting deleted_at timestamp.
        
        For permanent deletion, use hard_delete().
        """
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at', 'updated_at'])
    
    def hard_delete(self, using=None, keep_parents=False):
        """
        Permanently delete the record from the database.
        
        WARNING: This cannot be undone!
        """
        super().delete(using=using, keep_parents=keep_parents)
    
    def restore(self):
        """Restore a soft-deleted record."""
        if self.deleted_at is not None:
            self.deleted_at = None
            self.save(update_fields=['deleted_at', 'updated_at'])


class CompanyOwnedModel(SoftDeleteModel):
    """
    Abstract model for records that belong to a specific company.
    
    Provides multi-tenant data isolation when combined with
    TenantMiddleware and appropriate permissions.
    """
    company = models.ForeignKey(
        'accounts.Company',
        on_delete=models.CASCADE,
        related_name='%(class)s_set',
        help_text="Company that owns this record"
    )
    
    class Meta:
        abstract = True
