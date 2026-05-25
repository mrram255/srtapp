"""Settings used only by pytest (`DJANGO_SETTINGS_MODULE=config.settings.test`)."""

from __future__ import annotations

import os

os.environ.setdefault(
    'DJANGO_SECRET_KEY',
    'test-django-secret-key-at-least-fifty-characters-long-xxxxxx',
)
os.environ.setdefault(
    'JWT_SECRET_KEY',
    'test-jwt-secret-key-at-least-fifty-characters-long-xxxxxx',
)

from pathlib import Path

from .base import *

DEBUG = False
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'pytest',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

_log_dir = BASE_DIR / 'logs'
_log_dir.mkdir(parents=True, exist_ok=True)
LOGGING['handlers']['audit_file']['filename'] = str(_log_dir / 'audit-test.log')

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
