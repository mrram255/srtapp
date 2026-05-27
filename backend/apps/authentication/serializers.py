from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.services import AuthService
from apps.authentication.validators import validate_new_password, validate_password_complexity

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs['email'].lower()
        request = self.context.get('request')
        user, requires_2fa = AuthService.authenticate(email, attrs['password'], request)

        if user is None:
            raise serializers.ValidationError({'non_field_errors': ['Invalid credentials.']})

        if user.is_locked():
            raise serializers.ValidationError(
                {'non_field_errors': ['Account is locked. Try again after 30 minutes.']}
            )

        if not user.is_active:
            raise serializers.ValidationError({'non_field_errors': ['Account is deactivated.']})

        attrs['user'] = user
        attrs['requires_2fa'] = requires_2fa
        return attrs


class TwoFactorVerifySerializer(serializers.Serializer):
    otp_code = serializers.RegexField(r'^\d{6}$')
    session_key = serializers.UUIDField()

    def validate(self, attrs):
        request = self.context['request']
        session = (
            AuthService  # noqa: placeholder for type hints
        )
        from apps.authentication.models import UserSession

        try:
            session = UserSession.objects.select_related('user').get(
                session_key=attrs['session_key'],
                is_active=False,
            )
        except UserSession.DoesNotExist:
            raise serializers.ValidationError({'session_key': ['Invalid or expired session.']}) from None

        user = session.user
        if not AuthService.verify_2fa_otp(user, attrs['otp_code'], attrs['session_key']):
            raise serializers.ValidationError({'otp_code': ['Invalid or expired OTP.']})

        attrs['user'] = user
        attrs['session'] = session
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    """Admin-only bulk user creation."""

    password = serializers.CharField(write_only=True, min_length=12)
    department = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'role',
            'department',
            'phone',
            'password',
        ]

    def validate_password(self, value):
        validate_password_complexity(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        phone = validated_data.pop('phone', None) or f'+9199{User.objects.count():08d}'
        return User.objects.create_user(password=password, phone=phone, **validated_data)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({'old_password': ['Old password is incorrect.']})
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': ['Passwords do not match.']})
        validate_new_password(user, attrs['new_password'])
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.RegexField(r'^\d{6}$')
    new_password = serializers.CharField(write_only=True, min_length=12)
    confirm_password = serializers.CharField(write_only=True, min_length=12)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': ['Passwords do not match.']})
        try:
            user = User.objects.get(email__iexact=attrs['email'], is_deleted=False)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': ['User not found.']}) from None
        if not AuthService.verify_password_reset_otp(user, attrs['otp_code']):
            raise serializers.ValidationError({'otp_code': ['Invalid or expired OTP.']})
        validate_new_password(user, attrs['new_password'])
        attrs['user'] = user
        return attrs


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate_refresh_token(self, value):
        try:
            token = RefreshToken(value)
        except Exception as exc:
            raise serializers.ValidationError('Invalid refresh token.') from exc
        self.context['refresh'] = token
        return value


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class UserSessionSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    session_key = serializers.UUIDField()
    ip_address = serializers.IPAddressField(allow_null=True)
    user_agent = serializers.CharField()
    device_type = serializers.CharField()
    location = serializers.CharField()
    is_active = serializers.BooleanField()
    last_activity = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
    expired_at = serializers.DateTimeField(allow_null=True)
