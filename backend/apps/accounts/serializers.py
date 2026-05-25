from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer with additional claims."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        from django.core.files.storage import default_storage
        def _url(path):
            if not path: return ''
            try:
                return default_storage.url(path)
            except Exception:
                return path

        data['user'] = {
            'id': str(self.user.id),
            'email': self.user.email,
            'role': self.user.role,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'college_id': str(self.user.college_id) if self.user.college else None,
            'department_id': str(self.user.department_id) if self.user.department else None,
            'profile_photo': _url(self.user.profile_photo),
            'signature': _url(self.user.signature),
            'is_verified': self.user.is_verified,
            'must_change_password': self.user.must_change_password,
        }

        return data


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    """Attach role/email claims to rotated access tokens."""

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = RefreshToken(attrs['refresh'])
        user = User.objects.get(pk=str(refresh['user_id']))
        access = refresh.access_token
        access['role'] = user.role
        access['email'] = user.email
        data['access'] = str(access)
        return data


class UserSerializer(serializers.ModelSerializer):
    profile_photo = serializers.SerializerMethodField()
    signature = serializers.SerializerMethodField()

    def _build_url(self, path):
        if not path:
            return ''
        try:
            from django.core.files.storage import default_storage
            url = default_storage.url(path)
            # Local storage returns relative URL — make absolute
            if url.startswith('/'):
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(url)
                from django.conf import settings
                base = getattr(settings, 'SITE_URL', 'http://localhost:8000')
                return f"{base}{url}"
            return url
        except Exception:
            return path

    def get_profile_photo(self, obj):
        return self._build_url(obj.profile_photo)

    def get_signature(self, obj):
        return self._build_url(obj.signature)

    """Serializer for User model."""

    college_name = serializers.CharField(source='college.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'phone',
            'role',
            'first_name',
            'last_name',
            'full_name',
            'profile_photo',
            'signature',
            'college',
            'college_name',
            'department',
            'department_name',
            'is_active',
            'is_verified',
            'two_factor_enabled',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'full_name']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""

    password = serializers.CharField(write_only=True, required=True, min_length=12)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'email',
            'phone',
            'role',
            'first_name',
            'last_name',
            'password',
            'confirm_password',
            'college',
            'department',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})

        try:
            validate_password(attrs['password'])
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': list(exc.messages)}) from exc

        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        return User.objects.create_user(password=password, **validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user details."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'profile_photo', 'department']


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=12)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'new_password': 'Passwords do not match.'})

        try:
            validate_password(attrs['new_password'])
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'new_password': list(exc.messages)}) from exc

        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value


class LoginSerializer(serializers.Serializer):
    """Serializer for login requests."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class RefreshTokenSerializer(serializers.Serializer):
    """Serializer for token refresh."""

    refresh = serializers.CharField(required=True)


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout requests."""

    refresh = serializers.CharField(required=True)


class StudentRegistrationSerializer(serializers.ModelSerializer):
    """Public self-registration for students."""

    password = serializers.CharField(write_only=True, required=True, min_length=12)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'email',
            'phone',
            'first_name',
            'last_name',
            'password',
            'confirm_password',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        try:
            validate_password(attrs['password'])
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': list(exc.messages)}) from exc
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        return User.objects.create_user(
            role='STUDENT',
            is_verified=False,
            password=password,
            **validated_data,
        )


class OTPVerifySerializer(serializers.Serializer):
    """Verify email OTP."""
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, min_length=6, max_length=6)


class ForgotPasswordSerializer(serializers.Serializer):
    """Request password reset OTP."""
    email = serializers.EmailField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    """Reset password using OTP."""
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, min_length=6, max_length=6)
    new_password = serializers.CharField(required=True, write_only=True, min_length=12)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'new_password': 'Passwords do not match.'})
        try:
            validate_password(attrs['new_password'])
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'new_password': list(exc.messages)}) from exc
        return attrs


class AvatarUploadSerializer(serializers.ModelSerializer):
    """Upload profile photo."""
    avatar = serializers.ImageField(write_only=True)

    class Meta:
        model = User
        fields = ['avatar']

    def update(self, instance, validated_data):
        avatar = validated_data.pop('avatar')
        instance.profile_photo = avatar.name
        instance.save(update_fields=['profile_photo'])
        return instance
