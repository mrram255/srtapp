"""End-to-end authentication flow integration tests."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_full_auth_flow_login_me_refresh_logout(api_client):
    user = User.objects.create_user(
        email='flow@example.com',
        phone='+919911111111',
        first_name='Flow',
        last_name='Test',
        role='ADMIN',
        password='ValidPass1!',
    )

    login = api_client.post(
        '/api/v1/auth/login/',
        {'email': user.email, 'password': 'ValidPass1!'},
        format='json',
    )
    assert login.status_code == 200
    access = login.data['data']['access']
    refresh = login.data['data']['refresh']

    me = api_client.get('/api/v1/auth/me/', HTTP_AUTHORIZATION=f'Bearer {access}')
    assert me.status_code == 200
    assert me.data['data']['email'] == user.email

    refreshed = api_client.post('/api/v1/auth/refresh/', {'refresh_token': refresh}, format='json')
    assert refreshed.status_code == 200
    assert refreshed.data['data']['access']

    logout = api_client.post(
        '/api/v1/auth/logout/',
        {'refresh_token': refresh},
        format='json',
        HTTP_AUTHORIZATION=f'Bearer {access}',
    )
    assert logout.status_code == 200


@pytest.mark.django_db
def test_full_2fa_flow(api_client):
    user = User.objects.create_user(
        email='flow2fa@example.com',
        phone='+919922222222',
        first_name='Flow',
        last_name='TwoFA',
        role='ADMIN',
        password='ValidPass1!',
        two_factor_enabled=True,
    )

    login = api_client.post(
        '/api/v1/auth/login/',
        {'email': user.email, 'password': 'ValidPass1!'},
        format='json',
    )
    assert login.status_code == 200
    assert login.data['data']['requires_2fa'] is True
    session_key = login.data['data']['session_key']

    from apps.authentication.models import OTPRecord

    otp = OTPRecord.objects.filter(user=user, purpose='login_2fa', is_used=False).latest('created_at').otp_code
    verify = api_client.post(
        '/api/v1/auth/verify-2fa/',
        {'otp_code': otp, 'session_key': session_key},
        format='json',
    )
    assert verify.status_code == 200
    assert verify.data['data']['access']
