from __future__ import annotations

import re
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.utils import timezone


PASSWORD_COMPLEXITY = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$'
)


def validate_password_complexity(password: str) -> None:
    if not PASSWORD_COMPLEXITY.match(password):
        raise ValidationError(
            'Password must be at least 8 characters and include uppercase, '
            'lowercase, digit, and special character.'
        )


def validate_password_not_reused(user, new_password: str, limit: int = 5) -> None:
    from apps.authentication.models import PasswordHistory

    if user.check_password(new_password):
        raise ValidationError('New password cannot be the same as the current password.')

    recent_hashes = PasswordHistory.objects.filter(user=user).order_by('-created_at')[:limit]
    for entry in recent_hashes:
        if check_password(new_password, entry.password_hash):
            raise ValidationError(f'Cannot reuse any of the last {limit} passwords.')


def validate_password_not_expired(user) -> None:
    expiry_days = getattr(settings, 'PASSWORD_EXPIRY_DAYS', 90)
    changed_at = getattr(user, 'password_changed_at', None)
    if changed_at and changed_at + timedelta(days=expiry_days) < timezone.now():
        raise ValidationError('Password has expired. Please reset your password.')


def validate_new_password(user, new_password: str) -> None:
    validate_password_complexity(new_password)
    validate_password_not_reused(user, new_password)
