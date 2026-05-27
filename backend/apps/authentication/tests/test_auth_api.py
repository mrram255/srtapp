from __future__ import annotations

import uuid

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient, APIRequestFactory

from apps.authentication.models import LoginAttempt, OTPRecord, PasswordHistory, UserSession
from apps.authentication.services import AuthService

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def request_factory():
    return APIRequestFactory()


def make_request(factory, user_agent='pytest'):
    request = factory.get('/api/v1/auth/me/')
    request.META['HTTP_USER_AGENT'] = user_agent
    request.META['REMOTE_ADDR'] = '127.0.0.1'
    return request


def create_user(**kwargs):
    defaults = {
        'email': 'authuser@example.com',
        'phone': '+919876543210',
        'first_name': 'Auth',
        'last_name': 'User',
        'role': 'ADMIN',
        'password': 'ValidPass123!',
    }
    defaults.update(kwargs)
    password = defaults.pop('password')
    return User.objects.create_user(password=password, **defaults)


@pytest.mark.django_db
class TestLogin:
    def test_login_success(self, api_client):
        user = create_user(email='login_ok@example.com', phone='+919876543211')
        response = api_client.post(
            '/api/v1/auth/login/',
            {'email': user.email, 'password': 'ValidPass123!'},
            format='json',
        )
        assert response.status_code == 200
        assert response.data['success'] is True
        assert response.data['data']['access']
        assert response.data['data']['refresh']
        assert response.data['data']['requires_2fa'] is False

    def test_login_wrong_password(self, api_client):
        user = create_user(email='login_bad@example.com', phone='+919876543212')
        response = api_client.post(
            '/api/v1/auth/login/',
            {'email': user.email, 'password': 'WrongPass123!'},
            format='json',
        )
        assert response.status_code == 400
        assert LoginAttempt.objects.filter(email=user.email, status='failed').exists()

    def test_login_user_not_found(self, api_client):
        response = api_client.post(
            '/api/v1/auth/login/',
            {'email': 'missing@example.com', 'password': 'ValidPass123!'},
            format='json',
        )
        assert response.status_code == 400

    def test_login_account_locked(self, api_client):
        user = create_user(email='locked@example.com', phone='+919876543213')
        user.failed_login_attempts = 5
        user.locked_until = timezone.now() + timezone.timedelta(minutes=30)
        user.save()
        response = api_client.post(
            '/api/v1/auth/login/',
            {'email': user.email, 'password': 'ValidPass123!'},
            format='json',
        )
        assert response.status_code == 400
        assert LoginAttempt.objects.filter(email=user.email, status='blocked').exists()

    def test_login_requires_2fa(self, api_client):
        user = create_user(email='twofa@example.com', phone='+919876543214', two_factor_enabled=True)
        response = api_client.post(
            '/api/v1/auth/login/',
            {'email': user.email, 'password': 'ValidPass123!'},
            format='json',
        )
        assert response.status_code == 200
        assert response.data['data']['requires_2fa'] is True
        assert response.data['data']['session_key']
        assert OTPRecord.objects.filter(user=user, purpose='login_2fa').exists()


@pytest.mark.django_db
class TestTwoFactor:
    def test_verify_2fa_success(self, api_client, request_factory):
        user = create_user(email='verify2fa@example.com', phone='+919876543215', two_factor_enabled=True)
        session = AuthService.create_session(user, make_request(request_factory), pending_2fa=True)
        otp = AuthService.generate_2fa_otp(user)
        response = api_client.post(
            '/api/v1/auth/verify-2fa/',
            {'otp_code': otp, 'session_key': str(session.session_key)},
            format='json',
        )
        assert response.status_code == 200
        assert response.data['data']['access']

    def test_verify_2fa_wrong_otp(self, api_client, request_factory):
        user = create_user(email='badotp@example.com', phone='+919876543216', two_factor_enabled=True)
        session = AuthService.create_session(user, make_request(request_factory), pending_2fa=True)
        AuthService.generate_2fa_otp(user)
        response = api_client.post(
            '/api/v1/auth/verify-2fa/',
            {'otp_code': '000000', 'session_key': str(session.session_key)},
            format='json',
        )
        assert response.status_code == 400

    def test_verify_2fa_expired_otp(self, api_client, request_factory):
        user = create_user(email='expired@example.com', phone='+919876543217', two_factor_enabled=True)
        session = AuthService.create_session(user, make_request(request_factory), pending_2fa=True)
        record = OTPRecord.objects.create(
            user=user,
            otp_code='123456',
            purpose='login_2fa',
            expires_at=timezone.now() - timezone.timedelta(minutes=1),
        )
        response = api_client.post(
            '/api/v1/auth/verify-2fa/',
            {'otp_code': record.otp_code, 'session_key': str(session.session_key)},
            format='json',
        )
        assert response.status_code == 400

    def test_verify_2fa_max_attempts(self, api_client, request_factory):
        user = create_user(email='maxattempt@example.com', phone='+919876543218', two_factor_enabled=True)
        session = AuthService.create_session(user, make_request(request_factory), pending_2fa=True)
        record = OTPRecord.objects.create(
            user=user,
            otp_code='654321',
            purpose='login_2fa',
            expires_at=timezone.now() + timezone.timedelta(minutes=5),
            attempts=5,
        )
        response = api_client.post(
            '/api/v1/auth/verify-2fa/',
            {'otp_code': record.otp_code, 'session_key': str(session.session_key)},
            format='json',
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestPassword:
    def test_change_password_success(self, api_client):
        user = create_user(email='changepw@example.com', phone='+919876543219')
        api_client.force_authenticate(user=user)
        response = api_client.post(
            '/api/v1/auth/password/change/',
            {
                'old_password': 'ValidPass123!',
                'new_password': 'NewValid123!',
                'confirm_password': 'NewValid123!',
            },
            format='json',
        )
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.check_password('NewValid123!')
        assert PasswordHistory.objects.filter(user=user).exists()

    def test_change_password_wrong_old(self, api_client):
        user = create_user(email='wrongold@example.com', phone='+919876543220')
        api_client.force_authenticate(user=user)
        response = api_client.post(
            '/api/v1/auth/password/change/',
            {
                'old_password': 'WrongPass123!',
                'new_password': 'NewValid123!',
                'confirm_password': 'NewValid123!',
            },
            format='json',
        )
        assert response.status_code == 400

    def test_change_password_reuse_blocked(self, api_client):
        user = create_user(email='reuse@example.com', phone='+919876543221')
        PasswordHistory.objects.create(user=user, password_hash=user.password)
        api_client.force_authenticate(user=user)
        response = api_client.post(
            '/api/v1/auth/password/change/',
            {
                'old_password': 'ValidPass123!',
                'new_password': 'ValidPass123!',
                'confirm_password': 'ValidPass123!',
            },
            format='json',
        )
        assert response.status_code == 400

    def test_password_reset_flow(self, api_client):
        user = create_user(email='reset@example.com', phone='+919876543222')
        api_client.post('/api/v1/auth/password/reset/', {'email': user.email}, format='json')
        otp = OTPRecord.objects.filter(user=user, purpose='password_reset').first().otp_code
        response = api_client.post(
            '/api/v1/auth/password/reset/confirm/',
            {
                'email': user.email,
                'otp_code': otp,
                'new_password': 'ResetPass123!',
                'confirm_password': 'ResetPass123!',
            },
            format='json',
        )
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.check_password('ResetPass123!')

    def test_password_complexity_rules(self, api_client):
        user = create_user(email='complex@example.com', phone='+919876543223')
        api_client.force_authenticate(user=user)
        response = api_client.post(
            '/api/v1/auth/password/change/',
            {
                'old_password': 'ValidPass123!',
                'new_password': 'short',
                'confirm_password': 'short',
            },
            format='json',
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestSessions:
    def test_create_and_list_sessions(self, api_client, request_factory):
        user = create_user(email='sessions@example.com', phone='+919876543224')
        api_client.force_authenticate(user=user)
        AuthService.create_session(user, make_request(request_factory))
        response = api_client.get('/api/v1/auth/sessions/')
        assert response.status_code == 200
        assert len(response.data['data']) >= 1

    def test_kill_session(self, api_client, request_factory):
        user = create_user(email='killsession@example.com', phone='+919876543225')
        api_client.force_authenticate(user=user)
        session = AuthService.create_session(user, make_request(request_factory))
        response = api_client.delete(f'/api/v1/auth/sessions/{session.id}/')
        assert response.status_code == 200
        session.refresh_from_db()
        assert session.is_active is False

    def test_invalidate_all_sessions(self, api_client, request_factory):
        user = create_user(email='killall@example.com', phone='+919876543226')
        AuthService.create_session(user, make_request(request_factory))
        AuthService.create_session(user, make_request(request_factory))
        count = AuthService.invalidate_all_sessions(user)
        assert count == 2


@pytest.mark.django_db
class TestAuthService:
    def test_check_account_lock(self, api_client):
        user = create_user(email='lockcheck@example.com', phone='+919876543232')
        user.failed_login_attempts = 5
        user.locked_until = timezone.now() + timezone.timedelta(minutes=30)
        user.save()
        assert AuthService.check_account_lock(user.email) is True

    def test_password_reset_unknown_email(self, api_client):
        response = api_client.post(
            '/api/v1/auth/password/reset/',
            {'email': 'unknown@example.com'},
            format='json',
        )
        assert response.status_code == 200

    def test_delete_missing_session(self, api_client):
        user = create_user(email='nosession@example.com', phone='+919876543233')
        api_client.force_authenticate(user=user)
        response = api_client.delete(f'/api/v1/auth/sessions/{uuid.uuid4()}/')
        assert response.status_code == 404


@pytest.mark.django_db
class TestPermissions:
    def test_me_requires_auth(self, api_client):
        response = api_client.get('/api/v1/auth/me/')
        assert response.status_code == 401

    def test_me_returns_profile(self, api_client):
        user = create_user(email='me@example.com', phone='+919876543227')
        api_client.force_authenticate(user=user)
        response = api_client.get('/api/v1/auth/me/')
        assert response.status_code == 200
        assert response.data['data']['email'] == user.email

    def test_register_requires_super_admin(self, api_client):
        user = create_user(email='notadmin@example.com', phone='+919876543228', role='TEACHER')
        api_client.force_authenticate(user=user)
        response = api_client.post(
            '/api/v1/auth/register/',
            {
                'email': 'newuser@example.com',
                'phone': '+919876543229',
                'first_name': 'New',
                'last_name': 'User',
                'role': 'STUDENT',
                'password': 'ValidPass123!',
            },
            format='json',
        )
        assert response.status_code == 403

    def test_logout_blacklists_token(self, api_client):
        user = create_user(email='logout@example.com', phone='+919876543230')
        login = api_client.post(
            '/api/v1/auth/login/',
            {'email': user.email, 'password': 'ValidPass123!'},
            format='json',
        )
        refresh = login.data['data']['refresh']
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['data']['access']}")
        response = api_client.post('/api/v1/auth/logout/', {'refresh_token': refresh}, format='json')
        assert response.status_code == 200

    def test_refresh_token(self, api_client):
        user = create_user(email='refresh@example.com', phone='+919876543231')
        login = api_client.post(
            '/api/v1/auth/login/',
            {'email': user.email, 'password': 'ValidPass123!'},
            format='json',
        )
        refresh = login.data['data']['refresh']
        response = api_client.post('/api/v1/auth/refresh/', {'refresh_token': refresh}, format='json')
        assert response.status_code == 200
        assert response.data['data']['access']
