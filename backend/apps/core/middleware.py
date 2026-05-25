from __future__ import annotations

import logging
import threading
import time

from django.utils.deprecation import MiddlewareMixin

from apps.core.utils import get_client_ip

logger = logging.getLogger('audit')
_thread_locals = threading.local()


def get_current_user():
    """Return user set by CurrentUserMiddleware for this thread."""
    return getattr(_thread_locals, 'user', None)


class CurrentUserMiddleware(MiddlewareMixin):
    """Expose request.user via threading.local()."""

    def process_request(self, request):
        _thread_locals.user = getattr(request, 'user', None)

    def process_response(self, request, response):
        if hasattr(_thread_locals, 'user'):
            del _thread_locals.user
        return response


class RequestTimingMiddleware(MiddlewareMixin):
    """Log response time for performance monitoring."""

    def process_request(self, request):
        request._start_time = time.perf_counter()

    def process_response(self, request, response):
        start = getattr(request, '_start_time', None)
        if start is not None:
            duration_ms = int((time.perf_counter() - start) * 1000)
            response['X-Response-Time-Ms'] = str(duration_ms)
            logger.info(
                'request_timing',
                extra={
                    'path': request.path,
                    'method': request.method,
                    'status_code': response.status_code,
                    'duration_ms': duration_ms,
                },
            )
        return response


class AuditLogMiddleware(MiddlewareMixin):
    """Log every API request for audit purposes."""

    def process_response(self, request, response):
        if not request.path.startswith('/api/'):
            return response

        user = getattr(request, 'user', None)
        user_id = str(user.pk) if user and user.is_authenticated else None
        duration_ms = None
        start = getattr(request, '_start_time', None)
        if start is not None:
            duration_ms = int((time.perf_counter() - start) * 1000)

        logger.info(
            'api_audit',
            extra={
                'user_id': user_id,
                'ip_address': get_client_ip(request),
                'endpoint': request.path,
                'method': request.method,
                'status_code': response.status_code,
                'duration_ms': duration_ms,
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            },
        )
        return response
