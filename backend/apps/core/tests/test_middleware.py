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


def test_audit_log_middleware_logs_api_requests(rf, monkeypatch):
    messages = []

    def fake_info(message, *args, **kwargs):
        messages.append(message)

    monkeypatch.setattr('apps.core.middleware.logger.info', fake_info)

    def get_response(request):
        from django.http import HttpResponse

        return HttpResponse('ok', status=200)

    middleware = AuditLogMiddleware(get_response)
    request = rf.get('/api/v1/auth/login/')
    request.META['REMOTE_ADDR'] = '127.0.0.1'
    middleware(request)
    assert 'api_audit' in messages
