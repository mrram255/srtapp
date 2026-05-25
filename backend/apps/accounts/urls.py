from django.urls import path

from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    PasswordChangeView,
    UserCreateView,
    UserDetailView,
    UserListView,
    UserProfileView,
    StudentRegistrationView,
    VerifyEmailView,
    ResendVerificationEmailView,
    ForgotPasswordView,
    ResetPasswordView,
    AvatarUploadView,
    ChangePasswordView,
    UserSignatureUploadView,

)

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),
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
