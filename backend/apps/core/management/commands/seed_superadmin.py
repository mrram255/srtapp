from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create or update the default super admin user.'

    def add_arguments(self, parser):
        parser.add_argument('--email', default='admin@srtapp.com')
        parser.add_argument('--password', default='AdminPass1!')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'phone': '+919999999990',
                'first_name': 'Super',
                'last_name': 'Admin',
                'role': 'SUPER_ADMIN',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.role = 'SUPER_ADMIN'
        user.save()
        verb = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f'{verb} super admin: {email}'))
