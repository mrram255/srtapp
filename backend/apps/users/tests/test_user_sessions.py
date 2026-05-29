from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APIRequestFactory

from apps.authentication.services import AuthService
from apps.users.models import Role

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def request_factory():
    return APIRequestFactory()


def _request(factory):
    request = factory.get('/')
    request.META['REMOTE_ADDR'] = '127.0.0.1'
    request.META['HTTP_USER_AGENT'] = 'pytest'
    return request


def _super_admin():
    role = Role.objects.get(name='super_admin')
    user = User.objects.create_user(
        email='sa-sessions@example.com',
        phone='+919900000201',
        first_name='Super',
        last_name='Admin',
        role='SUPER_ADMIN',
        role_ref=role,
        password='ValidPass123!',
    )
    user.set_password('ValidPass123!')
    user.save()
    return user


def _teacher():
    role = Role.objects.get(name='teacher')
    user = User.objects.create_user(
        email='teacher-sessions@example.com',
        phone='+919900000202',
        first_name='Tea',
        last_name='Cher',
        role='TEACHER',
        role_ref=role,
        password='ValidPass123!',
    )
    user.set_password('ValidPass123!')
    user.save()
    return user


@pytest.mark.django_db
class TestUserSessionsAdmin:
    def test_super_admin_lists_target_user_sessions(self, api_client, request_factory):
        admin = _super_admin()
        target = _teacher()
        AuthService.create_session(target, _request(request_factory))

        api_client.force_authenticate(user=admin)
        response = api_client.get(f'/api/v1/users/{target.id}/sessions/')

        assert response.status_code == 200
        assert len(response.data['data']) >= 1

    def test_super_admin_kills_target_session(self, api_client, request_factory):
        admin = _super_admin()
        target = _teacher()
        session = AuthService.create_session(target, _request(request_factory))

        api_client.force_authenticate(user=admin)
        response = api_client.post(
            f'/api/v1/users/{target.id}/sessions/kill/',
            {'session_id': str(session.id)},
            format='json',
        )

        assert response.status_code == 200
        session.refresh_from_db()
        assert session.is_active is False

    def test_teacher_cannot_list_other_sessions(self, api_client, request_factory):
        admin = _super_admin()
        target = _teacher()
        AuthService.create_session(target, _request(request_factory))

        api_client.force_authenticate(user=target)
        response = api_client.get(f'/api/v1/users/{admin.id}/sessions/')
        assert response.status_code == 403
