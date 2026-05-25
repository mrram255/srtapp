import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """Every model in SRTAPP MUST inherit this."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self, user=None):
        """Never hard-delete records. Always soft delete."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])

    def hard_delete(self, *args, **kwargs):
        """Only for testing - never use in production."""
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class CollegeScopedModel(BaseModel):
    """Models that belong to a specific college."""

    college = models.ForeignKey(
        'colleges.College',
        on_delete=models.CASCADE,
        db_index=True,
    )

    class Meta:
        abstract = True
