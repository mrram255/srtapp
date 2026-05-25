from django.urls import path

from .views import (
    AvatarUploadView,
    ChangePasswordView,
    ResendVerificationEmailView,
    ResetPasswordView,
    StudentRegistrationView,
    UserCreateView,
    UserDetailView,
    UserListView,
    UserProfileView,
    UserSignatureUploadView,
    VerifyEmailView,
    ForgotPasswordView,
)

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<uuid:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('register/', StudentRegistrationView.as_view(), name='student_register'),
    path('email/verify/', VerifyEmailView.as_view(), name='email_verify'),
    path('email/resend/', ResendVerificationEmailView.as_view(), name='email_resend'),
    path('password/forgot/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('password/reset/', ResetPasswordView.as_view(), name='reset_password'),
    path('avatar/upload/', AvatarUploadView.as_view(), name='avatar_upload'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('signature/upload/', UserSignatureUploadView.as_view(), name='signature_upload'),
]
