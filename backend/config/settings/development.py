from pathlib import Path

from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8081',
]

# Debug toolbar
INSTALLED_APPS += ['debug_toolbar', 'silk']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', 'silk.middleware.SilkyMiddleware']
INTERNAL_IPS = ['127.0.0.1']

# Silk profiling — keep text stats in Silk UI; disable binary `.prof` writes to MEDIA_ROOT.
# Docker / root-owned `backend/media/` often causes PermissionError for local runserver users.
SILKY_PYTHON_PROFILER = True
SILKY_PYTHON_PROFILER_BINARY = False

# Console email backend

# Disable secure cookies for local dev
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False


_log_dir = BASE_DIR / 'logs'
_log_dir.mkdir(parents=True, exist_ok=True)
LOGGING['handlers']['audit_file']['filename'] = str(_log_dir / 'audit.log')
