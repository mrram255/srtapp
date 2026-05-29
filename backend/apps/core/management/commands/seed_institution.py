from django.core.management.base import BaseCommand

from apps.colleges.models import AcademicYear, College, Department


class Command(BaseCommand):
    help = 'Seed a demo college with department and academic year.'

    def handle(self, *args, **options):
        college, _ = College.objects.get_or_create(
            code='SRT',
            defaults={
                'name': 'SRT College',
                'address': 'Main Campus',
                'city': 'Dhmari',
                'state': 'Maharashtra',
                'pincode': '413801',
                'phone': '+919999999999',
                'email': 'college@srtapp.com',
                'established_year': 1990,
            },
        )
        dept, _ = Department.objects.get_or_create(
            college=college,
            code='CSE',
            defaults={'name': 'Computer Science'},
        )
        AcademicYear.objects.get_or_create(
            college=college,
            year='2025-2026',
            defaults={
                'start_date': '2025-06-01',
                'end_date': '2026-05-31',
                'is_current': True,
            },
        )
        self.stdout.write(self.style.SUCCESS(f'Seeded institution: {college.name} / {dept.name}'))
