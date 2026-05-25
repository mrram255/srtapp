"""Reset known dev login passwords (local development only)."""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

DEFAULT_EMAILS = [
    'admin@srtapp.com',
    'mr.ram255@gmail.com',
    'rpsahnni@gmail.com',
]

DEFAULT_PASSWORD = 'Srtapp@123'


class Command(BaseCommand):
    help = 'Unlock dev users and set a known password (DEBUG only).'

    def add_arguments(self, parser):
        parser.add_argument('--password', default=DEFAULT_PASSWORD)
        parser.add_argument('--email', action='append', dest='emails')

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stderr.write('Refusing to run outside DEBUG mode.')
            return

        User = get_user_model()
        emails = options['emails'] or DEFAULT_EMAILS
        password = options['password']

        for email in emails:
            user = User.objects.filter(email__iexact=email).first()
            if not user:
                self.stdout.write(self.style.WARNING(f'Skip (not found): {email}'))
                continue
            user.set_password(password)
            user.is_active = True
            user.failed_login_attempts = 0
            user.locked_until = None
            user.two_factor_enabled = False
            user.save(
                update_fields=[
                    'password',
                    'is_active',
                    'failed_login_attempts',
                    'locked_until',
                    'two_factor_enabled',
                ]
            )
            self.stdout.write(self.style.SUCCESS(f'{email} -> password set, unlocked, 2FA off'))

        self.stdout.write(self.style.NOTICE(f'Login with email + password: {password}'))
