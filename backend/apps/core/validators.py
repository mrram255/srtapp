import re

import magic
from django.core.exceptions import ValidationError

ALLOWED_TYPES = {
    'document': [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ],
    'image': ['image/jpeg', 'image/png', 'image/webp'],
    'spreadsheet': [
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    ],
    'video': ['video/mp4', 'video/webm'],
    'avatar': ['image/jpeg', 'image/png', 'image/webp'],
}
MAX_FILE_SIZES = {
    'document': 10 * 1024 * 1024,
    'image': 5 * 1024 * 1024,
    'spreadsheet': 10 * 1024 * 1024,
    'video': 50 * 1024 * 1024,
    'avatar': 2 * 1024 * 1024,
}


def validate_upload(file, file_type: str) -> None:
    header = file.read(2048)
    file.seek(0)
    detected = magic.from_buffer(header, mime=True)
    allowed = ALLOWED_TYPES.get(file_type, [])
    if detected not in allowed:
        raise ValidationError(
            f"File type '{detected}' is not allowed for {file_type}. "
            f"Allowed: {', '.join(allowed)}"
        )

    max_size = MAX_FILE_SIZES.get(file_type, 5 * 1024 * 1024)
    if file.size > max_size:
        raise ValidationError(
            f"File too large ({file.size // 1024 // 1024}MB). "
            f"Max: {max_size // 1024 // 1024}MB"
        )

    safe_name = re.sub(r'[^\w\-_\.]', '_', file.name)
    safe_name = re.sub(r'\.{2,}', '.', safe_name)
    file.name = safe_name[:100]
