from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'
    rate = '5/min'


class PasswordResetRateThrottle(AnonRateThrottle):
    scope = 'password_reset'
    rate = '3/min'


class EmailVerifyRateThrottle(AnonRateThrottle):
    scope = 'email_verify'
    rate = '5/min'


class APIRateThrottle(UserRateThrottle):
    scope = 'user'
    rate = '100/min'
