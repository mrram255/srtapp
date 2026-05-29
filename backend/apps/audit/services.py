from __future__ import annotations

import logging
import uuid
from typing import Any

from django.conf import settings
from django.http import HttpRequest, HttpResponse

from apps.core.utils import get_client_ip

logger = logging.getLogger('audit')

_DEFAULT_SKIP_PATH_PREFIXES = (
    '/health/',
    '/api/v1/health/',
    '/__debug__/',
    '/silk/',
)

_HTTP_ACTION_MAP = {
    'GET': 'read',
    'HEAD': 'read',
    'OPTIONS': 'read',
    'POST': 'create',
    'PUT': 'update',
    'PATCH': 'update',
    'DELETE': 'delete',
}

# Maps URL segment (after /api/v1/) to AuditLog.module choice value.
_PATH_MODULE_MAP = {
    'auth': 'authentication',
    'authentication': 'authentication',
    'users': 'users',
    'profile': 'users',
    'institutions': 'institutions',
    'academic': 'academic',
    'academics': 'academic',
    'colleges': 'colleges',
    'students': 'students',
    'staff': 'staff',
    'teachers': 'teachers',
    'finance': 'finance',
    'accounts': 'finance',
    'certificates': 'certificates',
    'admissions': 'admissions',
    'notifications': 'notifications',
    'messages': 'notifications',
    'messaging': 'notifications',
    'audit': 'audit',
    'dashboard': 'dashboard',
    'analytics': 'dashboard',
}


def _skip_prefixes() -> tuple[str, ...]:
    configured = getattr(settings, 'AUDIT_LOG_SKIP_PATH_PREFIXES', None)
    if configured:
        return tuple(configured)
    return _DEFAULT_SKIP_PATH_PREFIXES


def should_skip_path(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in _skip_prefixes())


def resolve_module_from_path(path: str) -> str:
    parts = [segment for segment in path.strip('/').split('/') if segment]
    if len(parts) >= 3 and parts[0] == 'api' and parts[1].startswith('v'):
        segment = parts[2].replace('-', '_')
        return _PATH_MODULE_MAP.get(segment, 'other')
    return 'system'


def resolve_action(method: str, path: str) -> str:
    path_lower = path.lower()
    if method.upper() == 'POST' and '/login' in path_lower:
        return 'login'
    if method.upper() == 'POST' and '/logout' in path_lower:
        return 'logout'
    if '/export' in path_lower:
        return 'export'
    if '/import' in path_lower or '/bulk' in path_lower:
        return 'import'
    if '/approve' in path_lower:
        return 'approve'
    if '/reject' in path_lower:
        return 'reject'
    return _HTTP_ACTION_MAP.get(method.upper(), 'read')


def resolve_object_id(path: str) -> uuid.UUID | None:
    for segment in reversed(path.rstrip('/').split('/')):
        if not segment:
            continue
        try:
            return uuid.UUID(segment)
        except ValueError:
            continue
    return None


def log_api_request(
    request: HttpRequest,
    response: HttpResponse,
    *,
    duration_ms: int | None = None,
) -> None:
    """Persist API audit row and mirror to file logger."""
    path = request.path
    if not path.startswith('/api/') or should_skip_path(path):
        return

    user = getattr(request, 'user', None)
    user_id = None
    if user is not None and getattr(user, 'is_authenticated', False):
        user_id = user.pk

    action = resolve_action(request.method, path)
    module = resolve_module_from_path(path)
    object_id = resolve_object_id(path)

    ip_address = get_client_ip(request)
    logger.info(
        'api_audit',
        extra={
            'user_id': user_id,
            'audit_action': action,
            'audit_module': module,
            'request_method': request.method.upper()[:10],
            'request_path': path[:500],
            'response_status': response.status_code,
            'duration_ms': duration_ms,
            'ip_address': ip_address,
        },
    )

    if not getattr(settings, 'AUDIT_LOG_DB_ENABLED', True):
        return

    from apps.audit.models import AuditLog

    try:
        AuditLog.objects.create(
            user_id=user_id,
            action=action,
            module=module,
            model_name='',
            object_id=object_id,
            object_repr=path[:255],
            changes={},
            ip_address=ip_address,
            user_agent=(request.META.get('HTTP_USER_AGENT') or '')[:2000],
            request_method=request.method.upper()[:10],
            request_path=path[:500],
            response_status=response.status_code,
            duration_ms=duration_ms,
            metadata={'query': request.META.get('QUERY_STRING', '')},
            is_active=True,
        )
    except Exception:
        logger.exception('audit_db_write_failed', extra={'path': path})


def log_model_change(
    *,
    user,
    action: str,
    module: str,
    model_name: str,
    object_id: uuid.UUID | None,
    object_repr: str,
    changes: dict[str, Any] | None = None,
    request: HttpRequest | None = None,
    metadata: dict[str, Any] | None = None,
):
    """Record domain model create/update/delete (explicit calls, not signals)."""
    from apps.audit.models import AuditLog

    if not getattr(settings, 'AUDIT_LOG_DB_ENABLED', True):
        return None

    valid_modules = dict(AuditLog.MODULE_CHOICES)
    module_value = module if module in valid_modules else 'other'

    ip_address = None
    user_agent = ''
    request_method = ''
    request_path = ''
    if request is not None:
        ip_address = get_client_ip(request)
        user_agent = (request.META.get('HTTP_USER_AGENT') or '')[:2000]
        request_method = request.method.upper()[:10]
        request_path = request.path[:500]

    user_id = None
    if user is not None and getattr(user, 'is_authenticated', False):
        user_id = user.pk

    return AuditLog.objects.create(
        user_id=user_id,
        action=action,
        module=module_value,
        model_name=model_name[:100],
        object_id=object_id,
        object_repr=object_repr[:255],
        changes=changes or {},
        ip_address=ip_address,
        user_agent=user_agent,
        request_method=request_method,
        request_path=request_path,
        response_status=None,
        duration_ms=None,
        metadata=metadata or {},
        is_active=True,
    )
