from __future__ import annotations

import logging
import random
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.models import LoginAttempt, OTPRecord, PasswordHistory, UserSession
from apps.authentication.validators import validate_new_password
from apps.core.utils import get_client_ip

User = get_user_model()
logger = logging.getLogger('audit')


def detect_device_type(user_agent: str) -> str:
    ua = (user_agent or '').lower()
    if 'mobile' in ua or 'android' in ua or 'iphone' in ua:
        return 'mobile'
    if 'tablet' in ua or 'ipad' in ua:
        return 'tablet'
    return 'web'


class AuthService:
    OTP_EXPIRY_MINUTES = 5
    MAX_FAILED_ATTEMPTS = 5
    LOCK_MINUTES = 30

    @classmethod
    def check_account_lock(cls, email: str) -> bool:
        try:
            user = User.objects.get(email__iexact=email, is_deleted=False)
        except User.DoesNotExist:
            return False
        return user.is_locked()

    @classmethod
    def authenticate(cls, email: str, password: str, request=None):
        ip_address = get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500] if request else ''

        try:
            user = User.objects.get(email__iexact=email, is_deleted=False)
        except User.DoesNotExist:
            LoginAttempt.objects.create(
                email=email.lower(),
                ip_address=ip_address,
                user_agent=user_agent,
                status='failed',
                failure_reason='user_not_found',
            )
            return None, False

        if user.is_locked():
            LoginAttempt.objects.create(
                email=user.email,
                ip_address=ip_address,
                user_agent=user_agent,
                status='blocked',
                failure_reason='account_locked',
            )
            return user, False

        if not user.check_password(password):
            user.increment_failed_login()
            LoginAttempt.objects.create(
                email=user.email,
                ip_address=ip_address,
                user_agent=user_agent,
                status='failed',
                failure_reason='wrong_password',
            )
            return None, False

        if not user.is_active:
            LoginAttempt.objects.create(
                email=user.email,
                ip_address=ip_address,
                user_agent=user_agent,
                status='failed',
                failure_reason='inactive_account',
            )
            return None, False

        user.reset_failed_login()
        requires_2fa = bool(getattr(user, 'two_factor_enabled', False))
        LoginAttempt.objects.create(
            email=user.email,
            ip_address=ip_address,
            user_agent=user_agent,
            status='success',
        )
        return user, requires_2fa

    @classmethod
    def generate_tokens(cls, user):
        refresh = RefreshToken.for_user(user)
        refresh['role'] = user.role
        refresh['email'] = user.email
        return {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }

    @classmethod
    def _create_otp(cls, user, purpose: str) -> OTPRecord:
        OTPRecord.objects.filter(user=user, purpose=purpose, is_used=False).update(is_used=True)
        otp_code = f'{random.randint(0, 999999):06d}'
        return OTPRecord.objects.create(
            user=user,
            otp_code=otp_code,
            purpose=purpose,
            expires_at=timezone.now() + timedelta(minutes=cls.OTP_EXPIRY_MINUTES),
        )

    @classmethod
    def generate_2fa_otp(cls, user) -> str:
        record = cls._create_otp(user, 'login_2fa')
        cls._send_otp_email(user, record.otp_code, 'login_2fa')
        return record.otp_code

    @classmethod
    def generate_password_reset_otp(cls, user) -> str:
        record = cls._create_otp(user, 'password_reset')
        cls._send_otp_email(user, record.otp_code, 'password_reset')
        return record.otp_code

    @classmethod
    def verify_2fa_otp(cls, user, otp_code: str, session_key: uuid.UUID | str | None = None) -> bool:
        record = OTPRecord.objects.filter(
            user=user,
            purpose='login_2fa',
            is_used=False,
        ).order_by('-created_at').first()

        if not record or not record.is_valid():
            return False

        if record.otp_code != otp_code:
            record.mark_attempt()
            return False

        record.is_used = True
        record.save(update_fields=['is_used'])

        if session_key:
            UserSession.objects.filter(session_key=session_key, user=user).update(is_active=True)
        return True

    @classmethod
    def verify_password_reset_otp(cls, user, otp_code: str) -> bool:
        record = OTPRecord.objects.filter(
            user=user,
            purpose='password_reset',
            is_used=False,
        ).order_by('-created_at').first()

        if not record or not record.is_valid():
            return False

        if record.otp_code != otp_code:
            record.mark_attempt()
            return False

        record.is_used = True
        record.save(update_fields=['is_used'])
        return True

    @classmethod
    def create_session(cls, user, request, *, pending_2fa: bool = False) -> UserSession:
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        session = UserSession.objects.create(
            user=user,
            ip_address=get_client_ip(request),
            user_agent=user_agent,
            device_type=detect_device_type(user_agent),
            is_active=not pending_2fa,
            expired_at=timezone.now() + timedelta(days=7),
        )
        user.last_login_ip = session.ip_address
        user.last_login_device = user_agent[:200]
        user.last_login = timezone.now()
        user.save(update_fields=['last_login_ip', 'last_login_device', 'last_login'])
        return session

    @classmethod
    def invalidate_session(cls, session_key) -> bool:
        updated = UserSession.objects.filter(session_key=session_key, is_active=True).update(
            is_active=False,
            expired_at=timezone.now(),
        )
        return updated > 0

    @classmethod
    def invalidate_all_sessions(cls, user) -> int:
        return UserSession.objects.filter(user=user, is_active=True).update(
            is_active=False,
            expired_at=timezone.now(),
        )

    @classmethod
    def change_password(cls, user, new_password: str) -> None:
        validate_new_password(user, new_password)
        PasswordHistory.objects.create(user=user, password_hash=user.password)
        user.set_password(new_password)
        user.save()

    @classmethod
    def reset_password(cls, user, new_password: str) -> None:
        validate_new_password(user, new_password)
        PasswordHistory.objects.create(user=user, password_hash=user.password)
        user.set_password(new_password)
        user.save()
        cls.invalidate_all_sessions(user)

    @classmethod
    def build_user_payload(cls, user, request=None) -> dict:
        from django.core.files.storage import default_storage

        def _url(path: str) -> str:
            if not path:
                return ''
            try:
                url = default_storage.url(path)
                if url.startswith('/') and request:
                    return request.build_absolute_uri(url)
                return url
            except Exception:
                return path

        return {
            'id': str(user.id),
            'email': user.email,
            'role': user.role,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'college_id': str(user.college_id) if user.college_id else None,
            'department_id': str(user.department_id) if user.department_id else None,
            'profile_photo': _url(user.profile_photo),
            'signature': _url(getattr(user, 'signature', '')),
            'is_verified': user.is_verified,
            'two_factor_enabled': user.two_factor_enabled,
            'must_change_password': user.must_change_password,
        }

    @classmethod
    def _send_otp_email(cls, user, otp_code: str, purpose: str) -> None:
        try:
            from apps.accounts.emails import send_otp_email

            if purpose == 'login_2fa':
                from django.core.mail import send_mail

                send_mail(
                    subject='SRT App — Login Verification OTP',
                    message=f'Your login OTP is {otp_code}. Valid for {cls.OTP_EXPIRY_MINUTES} minutes.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            else:
                send_otp_email(user, otp_code, purpose)
        except Exception:
            logger.exception('otp_email_failed', extra={'user_id': str(user.id), 'purpose': purpose})
