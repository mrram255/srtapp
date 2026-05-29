from __future__ import annotations

import pytest

from apps.core.middleware import (
    AuditLogMiddleware,
    CurrentUserMiddleware,
    RequestTimingMiddleware,
    get_current_user,
)


@pytest.mark.django_db
def test_current_user_middleware_sets_thread_local(rf):
    middleware = CurrentUserMiddleware(lambda request: None)
    request = rf.get('/api/v1/users/')
    request.user = object()
    middleware.process_request(request)
    assert get_current_user() is request.user
    middleware.process_response(request, object())


def test_request_timing_middleware_adds_header(rf):
    def get_response(request):
        from django.http import HttpResponse

        return HttpResponse('ok')

    middleware = RequestTimingMiddleware(get_response)
    request = rf.get('/api/v1/health/')
    response = middleware(request)
    assert 'X-Response-Time-Ms' in response


@pytest.mark.django_db
def test_audit_log_middleware_logs_api_requests(rf):
    from apps.audit.models import AuditLog

    def get_response(request):
        from django.http import HttpResponse

        return HttpResponse('ok', status=200)

    middleware = AuditLogMiddleware(get_response)
    request = rf.get('/api/v1/students/')
    request.META['REMOTE_ADDR'] = '127.0.0.1'
    request.META['HTTP_USER_AGENT'] = 'pytest'
    request.user = type('Anon', (), {'is_authenticated': False})()
    middleware(request)
    assert AuditLog.objects.filter(request_path='/api/v1/students/', module='students').exists()
