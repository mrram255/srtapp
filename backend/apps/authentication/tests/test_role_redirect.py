from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.users.models import Role

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestRoleRedirectPayload:
    def test_login_includes_role_slug_from_role_ref(self, api_client):
        role = Role.objects.get(name='registrar')
        user = User.objects.create_user(
            email='registrar@example.com',
            phone='+919900000101',
            first_name='Reg',
            last_name='Istrar',
            role=role.name.upper(),
            role_ref=role,
            password='ValidPass123!',
        )

        response = api_client.post(
            '/api/v1/auth/login/',
            {'email': user.email, 'password': 'ValidPass123!'},
            format='json',
        )

        assert response.status_code == 200
        user_data = response.data['data']['user']
        assert user_data['role'] == 'REGISTRAR'
        assert user_data['role_slug'] == 'registrar'

    def test_jwt_access_contains_role_slug(self, api_client):
        role = Role.objects.get(name='super_admin')
        user = User.objects.create_user(
            email='super2@example.com',
            phone='+919900000102',
            first_name='Super',
            last_name='Admin',
            role=role.name.upper(),
            role_ref=role,
            password='ValidPass123!',
        )

        response = api_client.post(
            '/api/v1/auth/login/',
            {'email': user.email, 'password': 'ValidPass123!'},
            format='json',
        )

        assert response.status_code == 200
        access = response.data['data']['access']
        from rest_framework_simplejwt.tokens import AccessToken

        token = AccessToken(access)
        assert token['role_slug'] == 'super_admin'
