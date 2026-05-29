from __future__ import annotations

import uuid

import pytest
from django.http import HttpResponse

from apps.audit.models import AuditLog
from apps.audit.services import (
    log_api_request,
    log_model_change,
    resolve_action,
    resolve_module_from_path,
    resolve_object_id,
    should_skip_path,
)


def test_resolve_module_from_path():
    assert resolve_module_from_path('/api/v1/students/') == 'students'
    assert resolve_module_from_path('/api/v1/auth/login/') == 'authentication'
    assert resolve_module_from_path('/api/v1/unknown-app/') == 'other'


def test_resolve_action_login_and_crud():
    assert resolve_action('POST', '/api/v1/auth/login/') == 'login'
    assert resolve_action('POST', '/api/v1/auth/logout/') == 'logout'
    assert resolve_action('GET', '/api/v1/users/') == 'read'
    assert resolve_action('DELETE', '/api/v1/users/abc/') == 'delete'


def test_resolve_object_id_from_path():
    sample = uuid.uuid4()
    assert resolve_object_id(f'/api/v1/users/{sample}/') == sample
    assert resolve_object_id('/api/v1/users/') is None


def test_should_skip_health_paths():
    assert should_skip_path('/health/') is True
    assert should_skip_path('/api/v1/students/') is False


@pytest.mark.django_db
def test_log_api_request_creates_row(rf):
    request = rf.get('/api/v1/users/')
    request.META['REMOTE_ADDR'] = '10.0.0.1'
    request.META['HTTP_USER_AGENT'] = 'pytest'
    request.user = type('Anon', (), {'is_authenticated': False})()

    response = HttpResponse('ok', status=200)
    log_api_request(request, response, duration_ms=12)

    row = AuditLog.objects.get()
    assert row.module == 'users'
    assert row.action == 'read'
    assert row.request_method == 'GET'
    assert row.response_status == 200
    assert row.duration_ms == 12
    assert row.ip_address == '10.0.0.1'


@pytest.mark.django_db
def test_log_api_request_skips_health(rf):
    request = rf.get('/health/')
    response = HttpResponse('ok', status=200)
    log_api_request(request, response)
    assert AuditLog.objects.count() == 0


@pytest.mark.django_db
def test_log_model_change_persists_changes(super_admin_user):
    target_id = uuid.uuid4()
    row = log_model_change(
        user=super_admin_user,
        action='update',
        module='students',
        model_name='Student',
        object_id=target_id,
        object_repr='Student #1',
        changes={'status': {'old': 'active', 'new': 'suspended'}},
    )
    assert row is not None
    assert row.user_id == super_admin_user.id
    assert row.changes['status']['new'] == 'suspended'
