from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Print pg_dump command for manual database backup (stub).'

    def handle(self, *args, **options):
        db = settings.DATABASES['default']
        cmd = (
            f"pg_dump -h {db.get('HOST', 'localhost')} -U {db.get('USER', 'postgres')} "
            f"-d {db.get('NAME', 'srtapp')} > backup.sql"
        )
        self.stdout.write('Run the following on your host:')
        self.stdout.write(cmd)
