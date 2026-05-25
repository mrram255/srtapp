from __future__ import annotations

from django.db import models

from apps.core.models import TimeStampedModel


class Role(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True, db_index=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_system_role = models.BooleanField(default=False)
    permissions = models.ManyToManyField(
        'ModulePermission',
        through='RolePermission',
        related_name='roles',
        blank=True,
    )

    class Meta:
        db_table = 'users_roles'
        ordering = ['display_name']

    def __str__(self):
        return self.display_name


class Module(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True, db_index=True)
    display_name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)
    parent_module = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='children',
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'users_modules'
        ordering = ['order', 'display_name']

    def __str__(self):
        return self.display_name


class ModulePermission(TimeStampedModel):
    ACTION_CHOICES = [
        ('view', 'View'),
        ('create', 'Create'),
        ('edit', 'Edit'),
        ('delete', 'Delete'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('approve', 'Approve'),
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='permissions')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'users_module_permissions'
        unique_together = [('module', 'action')]
        ordering = ['module__order', 'action']

    def __str__(self):
        return f'{self.module.name}:{self.action}'


class RolePermission(models.Model):
    id = models.BigAutoField(primary_key=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    module_permission = models.ForeignKey(
        ModulePermission,
        on_delete=models.CASCADE,
        related_name='role_permissions',
    )
    field_restrictions = models.JSONField(default=dict, blank=True)
    record_restrictions = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'users_role_permissions'
        unique_together = [('role', 'module_permission')]


class UserActivity(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('export', 'Export'),
        ('import', 'Import'),
    ]

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='activities',
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    module = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'users_activity'
        ordering = ['-created_at']
