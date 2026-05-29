from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Run basic health checks (database connectivity).'

    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            self.stdout.write(self.style.SUCCESS('Database: OK'))
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f'Database: FAIL ({exc})'))
            raise SystemExit(1) from exc
