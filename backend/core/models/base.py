"""
Base models for the entire application.
"""
import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted objects by default."""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    
    def all_with_deleted(self):
        return super().get_queryset()
    
    def deleted_only(self):
        return super().get_queryset().filter(is_deleted=True)


class BaseModel(models.Model):
    """Abstract base model with common fields."""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text='UUID v4 unique identifier'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='Date and time when the object was created'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Date and time when the object was last updated'
    )
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Soft delete flag'
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Date and time when the object was soft deleted'
    )
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
        get_latest_by = 'created_at'
    
    def soft_delete(self):
        """Soft delete the object."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])
    
    def restore(self):
        """Restore a soft-deleted object."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])
    
    def hard_delete(self):
        """Permanently delete the object."""
        super().delete()


class AuditModel(BaseModel):
    """Abstract model that adds audit trail."""
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        help_text='User who created the object'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        help_text='User who last updated the object'
    )
    
    class Meta:
        abstract = True


class MetaDataModel(BaseModel):
    """Abstract model that adds metadata fields."""
    
    meta_data = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional metadata stored as JSON'
    )
    notes = models.TextField(
        blank=True,
        help_text='Notes or comments about this object'
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text='Tags for categorization and searching'
    )
    
    class Meta:
        abstract = True
