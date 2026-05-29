from __future__ import annotations

import pytest

from apps.audit.models import AuditLog
from apps.core.middleware import AuditLogMiddleware


@pytest.mark.django_db
def test_audit_log_middleware_persists_api_request(rf):
    def get_response(request):
        from django.http import HttpResponse

        request._start_time = 0
        return HttpResponse('ok', status=200)

    middleware = AuditLogMiddleware(get_response)
    request = rf.get('/api/v1/auth/login/')
    request.META['REMOTE_ADDR'] = '127.0.0.1'
    request.META['HTTP_USER_AGENT'] = 'pytest-agent'
    request.user = type('Anon', (), {'is_authenticated': False})()

    middleware(request)

    assert AuditLog.objects.filter(request_path='/api/v1/auth/login/').exists()
    row = AuditLog.objects.get(request_path='/api/v1/auth/login/')
    assert row.action == 'read'
    assert row.module == 'authentication'
