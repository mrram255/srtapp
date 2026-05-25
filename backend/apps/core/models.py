import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """Base model every new SRTAPP model should inherit."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_by = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_created',
    )
    updated_by = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_updated',
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class OrderedModel(TimeStampedModel):
    """For models that require explicit ordering."""

    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        abstract = True
        ordering = ['order', '-created_at']


class BaseModel(models.Model):
    """
    Legacy base model used by existing apps (college-scoped modules).

    New modules should prefer TimeStampedModel. Kept separate to avoid
    field clashes with models that define their own is_active column.
    """

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


class CoreSampleRecord(TimeStampedModel):
    """Concrete model for core app migrations and tests."""

    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'core_sample_records'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
