from django.contrib import admin

from apps.authentication.models import LoginAttempt, OTPRecord, PasswordHistory, UserSession

admin.site.register(OTPRecord)
admin.site.register(UserSession)
admin.site.register(LoginAttempt)
admin.site.register(PasswordHistory)
