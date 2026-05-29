from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

from apps.audit.models import AuditLog
from apps.audit.tests.conftest import auth_client
from apps.users.models import Role

User = get_user_model()


def _create_teacher():
    role = Role.objects.filter(name='teacher').first()
    user = User.objects.create_user(
        email='teacher-audit@example.com',
        phone='+919933344455',
        first_name='Tea',
        last_name='Cher',
        role='TEACHER',
        role_ref=role,
        password='ValidPass1!',
    )
    user.set_password('ValidPass1!')
    user.save()
    return user


@pytest.mark.django_db
class TestAuditLogAPI:
    def test_super_admin_can_list_logs(self, api_client, super_admin_user):
        AuditLog.objects.create(
            action='read',
            module='users',
            request_method='GET',
            request_path='/api/v1/users/',
            response_status=200,
        )
        client = auth_client(api_client, super_admin_user)
        response = client.get('/api/v1/audit/logs/')
        assert response.status_code == 200
        assert response.data['success'] is True
        assert len(response.data['data']) >= 1

    def test_non_admin_forbidden(self, api_client):
        teacher = _create_teacher()
        AuditLog.objects.create(
            action='read',
            module='users',
            request_method='GET',
            request_path='/api/v1/users/',
            response_status=200,
        )
        client = auth_client(api_client, teacher)
        response = client.get('/api/v1/audit/logs/')
        assert response.status_code == 403

    def test_audit_stats(self, api_client, super_admin_user):
        AuditLog.objects.create(
            action='read',
            module='students',
            request_method='GET',
            request_path='/api/v1/students/',
            response_status=200,
        )
        client = auth_client(api_client, super_admin_user)
        response = client.get('/api/v1/audit/stats/')
        assert response.status_code == 200
        assert response.data['data']['total'] >= 1
