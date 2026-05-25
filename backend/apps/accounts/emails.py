from django.core.mail import send_mail
from django.conf import settings


def send_welcome_email(user, otp):
    subject = "Welcome to SRT App — Verify Your Email"
    message = f"""
Hello {user.first_name},

Welcome to SRT App! 🎉

Your account has been created successfully.

Please verify your email using this OTP:

    {otp}

This OTP is valid for 10 minutes.

If you did not create this account, please ignore this email.

Regards,
SRT App Team
"""
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def send_otp_email(user, otp, purpose):
    if purpose == 'password_reset':
        subject = "SRT App — Password Reset OTP"
        message = f"""
Hello {user.first_name},

You requested a password reset.

Your OTP is:

    {otp}

This OTP is valid for 10 minutes.

If you did not request this, please ignore this email.

Regards,
SRT App Team
"""
    else:
        subject = "SRT App — Email Verification OTP"
        message = f"""
Hello {user.first_name},

Your Email Verification OTP is:

    {otp}

This OTP is valid for 10 minutes.

Regards,
SRT App Team
"""
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
