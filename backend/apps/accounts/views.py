import logging

from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.core.responses import APIResponse
from apps.core.throttles import (
    EmailVerifyRateThrottle,
    LoginRateThrottle,
    PasswordResetRateThrottle,
)
from apps.core.views import BaseAPIView

from .serializers import (
    CustomTokenObtainPairSerializer,
    LoginSerializer,
    LogoutSerializer,
    PasswordChangeSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
    StudentRegistrationSerializer,
    OTPVerifySerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    AvatarUploadSerializer,
)

User = get_user_model()
logger = logging.getLogger('audit')
security_logger = logging.getLogger('security')


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view with rate limiting and security checks."""

    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                message='Invalid input.',
                errors=serializer.errors,
                status=400,
            )

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            security_logger.warning(
                {
                    'event': 'failed_login',
                    'email': email,
                    'reason': 'user_not_found',
                    'ip': self._get_client_ip(request),
                }
            )
            return APIResponse.error(message='Invalid credentials.', status=401)

        if user.is_deleted:
            return APIResponse.error(message='Invalid credentials.', status=401)

        if user.is_locked():
            security_logger.warning(
                {
                    'event': 'locked_account_login_attempt',
                    'user_id': str(user.id),
                    'ip': self._get_client_ip(request),
                }
            )
            return APIResponse.error(
                message='Account is locked. Try again after 30 minutes.',
                status=423,
            )

        if not user.check_password(password):
            user.increment_failed_login()
            security_logger.warning(
                {
                    'event': 'failed_login',
                    'user_id': str(user.id),
                    'reason': 'wrong_password',
                    'attempts': user.failed_login_attempts,
                    'ip': self._get_client_ip(request),
                }
            )
            return APIResponse.error(message='Invalid credentials.', status=401)

        if not user.is_active:
            return APIResponse.error(
                message='Account is deactivated. Contact admin.',
                status=403,
            )

        user.reset_failed_login()
        user.last_login_ip = self._get_client_ip(request)
        user.last_login_device = request.META.get('HTTP_USER_AGENT', '')[:200]
        user.save(update_fields=['last_login_ip', 'last_login_device'])

        response = super().post(request, *args, **kwargs)

        logger.info(
            {
                'event': 'successful_login',
                'user_id': str(user.id),
                'role': user.role,
                'ip': self._get_client_ip(request),
            }
        )

        return APIResponse.success(data=response.data, message='Login successful.')

    def _get_client_ip(self, request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', '')


class CustomTokenRefreshView(TokenRefreshView):
    """Custom token refresh view."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            return APIResponse.success(data=response.data, message='Token refreshed successfully.')
        except TokenError:
            return APIResponse.error(message='Invalid or expired refresh token.', status=401)


class LogoutView(BaseAPIView):
    """Logout view that blacklists refresh token."""

    permission_classes = [IsAuthenticated]
    allowed_roles = [
        'SUPER_ADMIN',
        'ADMIN',
        'HOD',
        'TEACHER',
        'STUDENT',
        'PARENT',
        'ACCOUNTANT',
        'LIBRARIAN',
        'SECURITY',
    ]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors, status=400)

        try:
            refresh_token = serializer.validated_data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()

            logger.info(
                {
                    'event': 'logout',
                    'user_id': str(request.user.id),
                    'ip': self._get_ip(request),
                }
            )

            return APIResponse.success(message='Logout successful.')
        except TokenError:
            return APIResponse.error(message='Invalid token.', status=400)


class UserProfileView(BaseAPIView):
    """Get/update current user profile."""

    allowed_roles = [
        'SUPER_ADMIN',
        'ADMIN',
        'HOD',
        'TEACHER',
        'STUDENT',
        'PARENT',
        'ACCOUNTANT',
        'LIBRARIAN',
        'SECURITY',
    ]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return APIResponse.success(data=serializer.data)

    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                data=UserSerializer(request.user).data,
                message='Profile updated successfully.',
            )
        return APIResponse.error(message='Invalid input.', errors=serializer.errors)


class PasswordChangeView(BaseAPIView):
    """Change password view."""

    allowed_roles = [
        'SUPER_ADMIN',
        'ADMIN',
        'HOD',
        'TEACHER',
        'STUDENT',
        'PARENT',
        'ACCOUNTANT',
        'LIBRARIAN',
        'SECURITY',
    ]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()

            logger.info(
                {
                    'event': 'password_change',
                    'user_id': str(request.user.id),
                    'ip': self._get_ip(request),
                }
            )

            return APIResponse.success(message='Password changed successfully.')
        return APIResponse.error(message='Invalid input.', errors=serializer.errors)


class UserListView(BaseAPIView):
    """List users (Admin/Super Admin only)."""

    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD']

    def get(self, request):
        queryset = User.objects.filter(is_deleted=False)

        queryset = self.scope_to_role(queryset, request.user)

        role = request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)

        is_active = request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return APIResponse.paginated(queryset, UserSerializer, request)


class UserDetailView(BaseAPIView):
    """Get/update/delete specific user."""

    allowed_roles = ['SUPER_ADMIN', 'ADMIN']

    def get(self, request, pk):
        try:
            user = User.objects.get(id=pk, is_deleted=False)
            if request.user.role != 'SUPER_ADMIN' and user.college != request.user.college:
                return APIResponse.error(message='Access denied.', status=403)
            serializer = UserSerializer(user)
            return APIResponse.success(data=serializer.data)
        except User.DoesNotExist:
            return APIResponse.error(message='User not found.', status=404)

    def patch(self, request, pk):
        try:
            user = User.objects.get(id=pk, is_deleted=False)
            if request.user.role != 'SUPER_ADMIN' and user.college != request.user.college:
                return APIResponse.error(message='Access denied.', status=403)

            serializer = UserUpdateSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return APIResponse.success(
                    data=UserSerializer(user).data,
                    message='User updated successfully.',
                )
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)
        except User.DoesNotExist:
            return APIResponse.error(message='User not found.', status=404)

    def delete(self, request, pk):
        try:
            user = User.objects.get(id=pk, is_deleted=False)
            if request.user.role != 'SUPER_ADMIN' and user.college != request.user.college:
                return APIResponse.error(message='Access denied.', status=403)

            if user == request.user:
                return APIResponse.error(message='Cannot delete your own account.', status=400)

            user.soft_delete(request.user)
            logger.info(
                {
                    'event': 'user_soft_delete',
                    'target_user_id': str(user.id),
                    'deleted_by': str(request.user.id),
                }
            )
            return APIResponse.success(message='User deleted successfully.')
        except User.DoesNotExist:
            return APIResponse.error(message='User not found.', status=404)


class UserCreateView(BaseAPIView):
    """Create new user (Admin/Super Admin only)."""

    allowed_roles = ['SUPER_ADMIN', 'ADMIN']

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            if request.user.role != 'SUPER_ADMIN':
                serializer.validated_data['college'] = request.user.college

            user = serializer.save()
            logger.info(
                {
                    'event': 'user_created',
                    'new_user_id': str(user.id),
                    'role': user.role,
                    'created_by': str(request.user.id),
                }
            )
            return APIResponse.success(
                data=UserSerializer(user).data,
                message='User created successfully.',
                status=201,
            )
        return APIResponse.error(message='Invalid input.', errors=serializer.errors)


class StudentRegistrationView(BaseAPIView):
    """Public student self-registration."""
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]
    allowed_roles = []

    def post(self, request):
        from .emails import send_welcome_email
        from .models import OTPVerification

        serializer = StudentRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                message='Invalid input.',
                errors=serializer.errors,
            )

        user = serializer.save()

        otp_obj = OTPVerification.generate(user, 'email_verify')

        try:
            send_welcome_email(user, otp_obj.otp)
        except Exception as e:
            logger.error({'event': 'welcome_email_failed', 'user_id': str(user.id), 'error': str(e)})

        logger.info({'event': 'student_registered', 'user_id': str(user.id)})

        return APIResponse.success(
            data={'email': user.email, 'message': 'OTP sent to your email.'},
            message='Registration successful. Please verify your email.',
            status=201,
        )


class VerifyEmailView(BaseAPIView):
    """Verify email using OTP."""
    permission_classes = [AllowAny]
    throttle_classes = [EmailVerifyRateThrottle]
    allowed_roles = []

    def post(self, request):
        from .models import OTPVerification

        serializer = OTPVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        try:
            user = User.objects.get(email=email, is_deleted=False)
        except User.DoesNotExist:
            return APIResponse.error(message='User not found.', status=404)

        otp_obj = OTPVerification.objects.filter(
            user=user, purpose='email_verify', is_used=False
        ).last()

        if not otp_obj or not otp_obj.is_valid():
            return APIResponse.error(message='OTP expired. Request a new one.', status=400)

        if otp_obj.otp != otp:
            return APIResponse.error(message='Invalid OTP.', status=400)

        otp_obj.is_used = True
        otp_obj.save(update_fields=['is_used'])

        user.is_verified = True
        user.save(update_fields=['is_verified'])

        logger.info({'event': 'email_verified', 'user_id': str(user.id)})

        return APIResponse.success(message='Email verified successfully. You can now login.')


class ResendVerificationEmailView(BaseAPIView):
    """Resend email verification OTP."""
    permission_classes = [AllowAny]
    throttle_classes = [EmailVerifyRateThrottle]
    allowed_roles = []

    def post(self, request):
        from .emails import send_welcome_email
        from .models import OTPVerification

        email = (request.data.get('email') or '').strip().lower()
        if not email:
            return APIResponse.error(message='Email is required.', status=400)

        try:
            user = User.objects.get(email=email, is_deleted=False)
        except User.DoesNotExist:
            return APIResponse.success(message='If this email exists, OTP has been sent.')

        if user.is_verified:
            return APIResponse.success(message='Email is already verified.')

        otp_obj = OTPVerification.generate(user, 'email_verify')
        try:
            send_welcome_email(user, otp_obj.otp)
        except Exception as e:
            logger.error({'event': 'verify_email_resend_failed', 'error': str(e)})

        return APIResponse.success(message='If this email exists, OTP has been sent.')


class ForgotPasswordView(BaseAPIView):
    """Send password reset OTP."""
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]
    allowed_roles = []

    def post(self, request):
        from .emails import send_otp_email
        from .models import OTPVerification

        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email, is_deleted=False)
            otp_obj = OTPVerification.generate(user, 'password_reset')
            try:
                send_otp_email(user, otp_obj.otp, 'password_reset')
            except Exception as e:
                logger.error({'event': 'reset_email_failed', 'error': str(e)})
        except User.DoesNotExist:
            pass

        return APIResponse.success(
            message='If this email exists, OTP has been sent.'
        )


class ResetPasswordView(BaseAPIView):
    """Reset password using OTP."""
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]
    allowed_roles = []

    def post(self, request):
        from .models import OTPVerification

        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(email=email, is_deleted=False)
        except User.DoesNotExist:
            return APIResponse.error(message='User not found.', status=404)

        otp_obj = OTPVerification.objects.filter(
            user=user, purpose='password_reset', is_used=False
        ).last()

        if not otp_obj or not otp_obj.is_valid():
            return APIResponse.error(message='OTP expired. Request a new one.', status=400)

        if otp_obj.otp != otp:
            return APIResponse.error(message='Invalid OTP.', status=400)

        otp_obj.is_used = True
        otp_obj.save(update_fields=['is_used'])

        user.set_password(new_password)
        user.save()

        logger.info({'event': 'password_reset', 'user_id': str(user.id)})

        return APIResponse.success(message='Password reset successful. You can now login.')


class AvatarUploadView(BaseAPIView):
    """Upload profile photo."""
    allowed_roles = [
        'SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER',
        'STUDENT', 'PARENT', 'ACCOUNTANT', 'LIBRARIAN', 'SECURITY',
    ]

    def post(self, request):
        import os
        from django.core.files.storage import default_storage

        avatar = request.FILES.get('avatar')
        if not avatar:
            return APIResponse.error(message='No file uploaded.', status=400)

        allowed_types = ['image/jpeg', 'image/png', 'image/webp']
        if avatar.content_type not in allowed_types:
            return APIResponse.error(
                message='Only JPEG, PNG, WebP allowed.', status=400
            )

        if avatar.size > 50 * 1024:
            return APIResponse.error(message='File size must be under 50KB.', status=400)

        ext = os.path.splitext(avatar.name)[1]
        filename = f'avatars/{request.user.id}{ext}'

        saved_path = default_storage.save(filename, avatar)

        request.user.profile_photo = saved_path
        request.user.save(update_fields=['profile_photo'])

        return APIResponse.success(
            data={'profile_photo': default_storage.url(saved_path)},
            message='Avatar uploaded successfully.',
        )


class UserSignatureUploadView(BaseAPIView):
    """Upload user signature — registration ke time use hoga."""
    allowed_roles = [
        'SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER',
        'STUDENT', 'PARENT', 'ACCOUNTANT', 'LIBRARIAN', 'SECURITY',
    ]

    def post(self, request):
        import os
        from django.core.files.storage import default_storage

        signature = request.FILES.get('signature')
        if not signature:
            return APIResponse.error(message='No file uploaded.', status=400)

        allowed_types = ['image/jpeg', 'image/png', 'image/webp']
        if signature.content_type not in allowed_types:
            return APIResponse.error(message='Only JPEG, PNG, WebP allowed.', status=400)

        if signature.size > 50 * 1024:
            return APIResponse.error(message='Signature must be under 50KB.', status=400)

        ext = os.path.splitext(signature.name)[1].lower()
        filename = f'signatures/{request.user.id}{ext}'

        if request.user.signature:
            try:
                default_storage.delete(request.user.signature)
            except Exception:
                pass

        saved_path = default_storage.save(filename, signature)
        request.user.signature = saved_path
        request.user.save(update_fields=['signature'])

        return APIResponse.success(
            data={'signature': saved_path},
            message='Signature uploaded successfully.',
        )


class ChangePasswordView(BaseAPIView):
    """Change password for logged in user."""
    allowed_roles = [
        'SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER',
        'STUDENT', 'PARENT', 'ACCOUNTANT', 'LIBRARIAN', 'SECURITY',
    ]

    def post(self, request):
        old_password = request.data.get('old_password', '')
        new_password = request.data.get('new_password', '')
        confirm_password = request.data.get('confirm_password', '')

        if not old_password or not new_password or not confirm_password:
            return APIResponse.error(message='All fields are required.', status=400)

        if not request.user.check_password(old_password):
            return APIResponse.error(message='Current password is incorrect.', status=400)

        if new_password != confirm_password:
            return APIResponse.error(message='Passwords do not match.', status=400)

        if len(new_password) < 12:
            return APIResponse.error(message='Password must be at least 12 characters.', status=400)

        request.user.set_password(new_password)
        request.user.save(update_fields=['password'])

        return APIResponse.success(message='Password changed successfully.')
