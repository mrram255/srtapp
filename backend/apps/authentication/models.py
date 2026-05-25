from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class OTPRecord(models.Model):
    PURPOSE_CHOICES = [
        ('login_2fa', 'Login 2FA'),
        ('password_reset', 'Password Reset'),
        ('email_verify', 'Email Verify'),
        ('phone_verify', 'Phone Verify'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='auth_otps',
    )
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, db_index=True)
    is_used = models.BooleanField(default=False, db_index=True)
    expires_at = models.DateTimeField(db_index=True)
    attempts = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'auth_otp_records'
        indexes = [
            models.Index(fields=['user', 'purpose', 'is_used']),
        ]
        ordering = ['-created_at']

    def is_valid(self) -> bool:
        return not self.is_used and self.expires_at > timezone.now() and self.attempts < 5

    def mark_attempt(self) -> None:
        self.attempts += 1
        self.save(update_fields=['attempts'])


class UserSession(models.Model):
    DEVICE_TYPES = [
        ('web', 'Web'),
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='auth_sessions',
    )
    session_key = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES, default='web')
    location = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    last_activity = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    expired_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'auth_user_sessions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]
        ordering = ['-last_activity']


class LoginAttempt(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('blocked', 'Blocked'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, db_index=True)
    failure_reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'auth_login_attempts'
        ordering = ['-created_at']


class PasswordHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_history',
    )
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'auth_password_history'
        ordering = ['-created_at']
