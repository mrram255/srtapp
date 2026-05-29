from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class AuditLog(TimeStampedModel):
    """Immutable audit trail for API requests and domain changes."""

    ACTION_CHOICES = [
        ('create', 'Create'),
        ('read', 'Read'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('generate', 'Generate'),
        ('send', 'Send'),
    ]

    MODULE_CHOICES = [
        ('authentication', 'Authentication'),
        ('users', 'Users'),
        ('institutions', 'Institutions'),
        ('academic', 'Academic'),
        ('colleges', 'Colleges'),
        ('students', 'Students'),
        ('staff', 'Staff'),
        ('teachers', 'Teachers'),
        ('finance', 'Finance'),
        ('certificates', 'Certificates'),
        ('admissions', 'Admissions'),
        ('notifications', 'Notifications'),
        ('governance', 'Governance'),
        ('audit', 'Audit'),
        ('dashboard', 'Dashboard'),
        ('system', 'System'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)
    module = models.CharField(max_length=50, choices=MODULE_CHOICES, default='other', db_index=True)
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.UUIDField(null=True, blank=True, db_index=True)
    object_repr = models.CharField(max_length=255, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_method = models.CharField(max_length=10, blank=True, db_index=True)
    request_path = models.CharField(max_length=500, blank=True, db_index=True)
    response_status = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['module', 'created_at']),
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['request_path', 'created_at']),
        ]

    def __str__(self) -> str:
        user_label = self.user_id or 'system'
        return f'{self.action} {self.module} ({user_label}) @ {self.created_at}'
