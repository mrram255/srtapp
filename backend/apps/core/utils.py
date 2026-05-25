from __future__ import annotations

import io
import logging
import random
import re
import string
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Iterable

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.utils import timezone

logger = logging.getLogger(__name__)


def generate_unique_code(prefix: str, length: int = 8) -> str:
    """Generate a unique alphanumeric code with prefix (e.g. enrollment/receipt numbers)."""
    safe_prefix = re.sub(r'[^A-Za-z0-9-]', '', prefix.upper()) or 'CODE'
    body_length = max(length, 4)
    alphabet = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choices(alphabet, k=body_length))
    return f'{safe_prefix}-{suffix}'


def get_current_academic_year():
    """Return the active academic year record, if configured."""
    try:
        from apps.academic.models import AcademicYear

        return AcademicYear.objects.filter(is_current=True, is_active=True).first()
    except Exception:
        try:
            from apps.colleges.models import AcademicYear

            return AcademicYear.objects.filter(is_current=True).first()
        except Exception:
            return None


def get_client_ip(request) -> str | None:
    """Extract client IP from request headers or REMOTE_ADDR."""
    if request is None:
        return None
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def validate_file_size(file: UploadedFile, max_size_mb: int) -> None:
    """Raise ValidationError if uploaded file exceeds max size."""
    if file is None:
        raise ValidationError('No file provided.')
    max_bytes = max_size_mb * 1024 * 1024
    if file.size > max_bytes:
        raise ValidationError(
            f'File size exceeds maximum allowed size of {max_size_mb} MB.'
        )


def validate_file_extension(file: UploadedFile, allowed_extensions: Iterable[str]) -> None:
    """Raise ValidationError if file extension is not allowed."""
    if file is None or not file.name:
        raise ValidationError('No file provided.')
    allowed = {ext.lower().lstrip('.') for ext in allowed_extensions}
    extension = file.name.rsplit('.', 1)[-1].lower() if '.' in file.name else ''
    if extension not in allowed:
        raise ValidationError(
            f'Invalid file type. Allowed extensions: {", ".join(sorted(allowed))}.'
        )


def send_notification(user, title: str, message: str, channel: str = 'in_app') -> bool:
    """Unified notification entry point."""
    from apps.core.services import NotificationService

    return NotificationService.send_notification(
        user=user,
        title=title,
        message=message,
        channels=[channel],
    )


def generate_qr_code(data: str) -> bytes:
    """Generate QR code PNG bytes for certificates/ID cards."""
    from apps.core.services import QRCodeService

    return QRCodeService.generate(data)


def format_indian_currency(amount: Decimal | float | int | str) -> str:
    """Format amount in Indian numbering style: ₹1,23,456.00."""
    value = Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    sign = '-' if value < 0 else ''
    value = abs(value)
    integer_part, _, fractional_part = f'{value:.2f}'.partition('.')
    if len(integer_part) > 3:
        head = integer_part[:-3]
        tail = integer_part[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        formatted = ','.join(groups + [tail])
    else:
        formatted = integer_part
    return f'{sign}₹{formatted}.{fractional_part}'


def calculate_age(dob: date) -> int:
    """Calculate age in full years from date of birth."""
    today = timezone.localdate()
    years = today.year - dob.year
    if (today.month, today.day) < (dob.month, dob.day):
        years -= 1
    return max(years, 0)


def mask_aadhaar(aadhaar: str) -> str:
    """Mask Aadhaar number, showing only last 4 digits."""
    digits = re.sub(r'\D', '', aadhaar or '')
    if len(digits) != 12:
        raise ValidationError('Aadhaar number must contain 12 digits.')
    return f'XXXX-XXXX-{digits[-4:]}'
