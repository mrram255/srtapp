from pathlib import Path

from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']
# Avoid accidental lockouts while iterating on login during local dev.
DISABLE_AUTH_THROTTLE = True
# Dev: allow any frontend origin (3000, 3002, etc.) to avoid CORS blocks during local work.
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:3001',
    'http://localhost:3002',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:3001',
    'http://127.0.0.1:3002',
    'http://localhost:8081',
]
# Allow any local dev port (3000, 3002, etc.) without editing CORS on every port change.
CORS_ALLOWED_ORIGIN_REGEXES = [
    r'^http://localhost:\d+$',
    r'^http://127\.0\.0\.1:\d+$',
]

# Debug toolbar
INSTALLED_APPS += ['django_extensions', 'debug_toolbar', 'silk']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', 'silk.middleware.SilkyMiddleware']
INTERNAL_IPS = ['127.0.0.1']

# Silk request logging only — cProfile conflicts with debug toolbar / hot reload.
SILKY_PYTHON_PROFILER = False
SILKY_PYTHON_PROFILER_BINARY = False

# Console email backend

# Disable secure cookies for local dev
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False


_log_dir = BASE_DIR / 'logs'
_log_dir.mkdir(parents=True, exist_ok=True)
LOGGING['handlers']['audit_file']['filename'] = str(_log_dir / 'audit.log')
