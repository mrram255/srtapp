from __future__ import annotations

import logging

from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.models import UserSession
from apps.authentication.serializers import (
    LoginSerializer,
    LogoutSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
    TwoFactorVerifySerializer,
    UserSessionSerializer,
)
from apps.authentication.services import AuthService
from apps.core.permissions import IsSuperAdmin
from apps.core.responses import APIResponse
from apps.core.throttles import LoginRateThrottle, PasswordResetRateThrottle

User = get_user_model()
logger = logging.getLogger('audit')


class AuthViewSet(viewsets.ViewSet):
    """Authentication endpoints."""

    def get_throttles(self):
        from django.conf import settings

        if getattr(settings, 'DISABLE_AUTH_THROTTLE', False):
            return []
        if self.action in {'login', 'verify_2fa'}:
            return [LoginRateThrottle()]
        if self.action in {'password_reset', 'password_reset_confirm'}:
            return [PasswordResetRateThrottle()]
        return []

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)

        user = serializer.validated_data['user']
        requires_2fa = serializer.validated_data['requires_2fa']

        if requires_2fa:
            session = AuthService.create_session(user, request, pending_2fa=True)
            AuthService.generate_2fa_otp(user)
            return APIResponse.success(
                data={
                    'requires_2fa': True,
                    'session_key': str(session.session_key),
                    'user_data': AuthService.build_user_payload(user, request),
                },
                message='Two-factor authentication required.',
            )

        session = AuthService.create_session(user, request)
        tokens = AuthService.generate_tokens(user)
        return APIResponse.success(
            data={
                'requires_2fa': False,
                'access': tokens['access_token'],
                'refresh': tokens['refresh_token'],
                'session_key': str(session.session_key),
                'user': AuthService.build_user_payload(user, request),
            },
            message='Login successful.',
        )

    @action(
        detail=False,
        methods=['post'],
        url_path='verify-2fa',
        permission_classes=[AllowAny],
    )
    def verify_2fa(self, request):
        serializer = TwoFactorVerifySerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)

        user = serializer.validated_data['user']
        session = serializer.validated_data['session']
        session.is_active = True
        session.save(update_fields=['is_active'])
        tokens = AuthService.generate_tokens(user)
        return APIResponse.success(
            data={
                'access': tokens['access_token'],
                'refresh': tokens['refresh_token'],
                'session_key': str(session.session_key),
                'user': AuthService.build_user_payload(user, request),
            },
            message='Two-factor verification successful.',
        )

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def refresh(self, request):
        serializer = RefreshTokenSerializer(data={'refresh_token': request.data.get('refresh_token') or request.data.get('refresh')})
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        try:
            refresh = serializer.context['refresh']
            data = {'access': str(refresh.access_token), 'refresh': str(refresh)}
            return APIResponse.success(data=data, message='Token refreshed successfully.')
        except TokenError:
            return APIResponse.error(message='Invalid or expired refresh token.', status=401)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[AllowAny],
        url_path='token/refresh',
    )
    def token_refresh(self, request):
        """Backward-compatible alias for existing frontend proxy."""
        return self.refresh(request)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        serializer = LogoutSerializer(data={'refresh_token': request.data.get('refresh_token') or request.data.get('refresh')})
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        try:
            token = RefreshToken(serializer.validated_data['refresh_token'])
            token.blacklist()
            AuthService.invalidate_all_sessions(request.user)
            return APIResponse.success(message='Logout successful.')
        except TokenError:
            return APIResponse.error(message='Invalid token.', status=400)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='me')
    def me(self, request):
        return APIResponse.success(data=AuthService.build_user_payload(request.user, request))

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='password/change',
    )
    def password_change(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        AuthService.change_password(request.user, serializer.validated_data['new_password'])
        return APIResponse.success(message='Password changed successfully.')

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[AllowAny],
        url_path='password/reset',
    )
    def password_reset(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        email = serializer.validated_data['email'].lower()
        try:
            user = User.objects.get(email__iexact=email, is_deleted=False)
            AuthService.generate_password_reset_otp(user)
        except User.DoesNotExist:
            pass
        return APIResponse.success(message='If this email exists, OTP has been sent.')

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[AllowAny],
        url_path='password/reset/confirm',
    )
    def password_reset_confirm(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        user = serializer.validated_data['user']
        AuthService.reset_password(user, serializer.validated_data['new_password'])
        return APIResponse.success(message='Password reset successful.')

    @action(detail=False, methods=['post'], permission_classes=[IsSuperAdmin])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data, context={'request': request, 'actor': request.user})
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        user = serializer.save()
        return APIResponse.success(
            data=AuthService.build_user_payload(user, request),
            message='User registered successfully.',
            status=201,
        )


class SessionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        sessions = UserSession.objects.filter(user=request.user, is_active=True)
        data = [
            {
                'id': str(item.id),
                'session_key': str(item.session_key),
                'ip_address': item.ip_address,
                'user_agent': item.user_agent,
                'device_type': item.device_type,
                'location': item.location,
                'is_active': item.is_active,
                'last_activity': item.last_activity,
                'created_at': item.created_at,
                'expired_at': item.expired_at,
            }
            for item in sessions
        ]
        return APIResponse.success(data=data)

    def destroy(self, request, pk=None):
        session = UserSession.objects.filter(user=request.user, pk=pk, is_active=True).first()
        if not session:
            return APIResponse.error(message='Session not found.', status=404)
        AuthService.invalidate_session(session.session_key)
        return APIResponse.success(message='Session terminated.')
