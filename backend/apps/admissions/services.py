from __future__ import annotations

import uuid

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.students.models import Student

from .models import AdmissionApplication


class AdmissionService:
    @staticmethod
    @transaction.atomic
    def enroll_application(application: AdmissionApplication, *, enrolled_by) -> Student:
        if application.status not in ('ACCEPTED', 'SHORTLISTED'):
            raise ValueError('Application must be accepted before enrollment.')

        if Student.objects.filter(user__email=application.email, college=application.college).exists():
            raise ValueError('A student with this email already exists.')

        user = User.objects.create_user(
            email=application.email,
            phone=application.phone,
            first_name=application.first_name,
            last_name=application.last_name,
            role='STUDENT',
            college=application.college,
            password=uuid.uuid4().hex[:12],
        )

        from apps.colleges.models import AcademicYear

        academic_year = AcademicYear.objects.filter(college=application.college, is_current=True).first()
        if not academic_year:
            academic_year = AcademicYear.objects.filter(college=application.college).first()
        if not academic_year:
            raise ValueError('No academic year configured for this college.')

        enrollment_number = f'ENR-{application.application_number}'
        student = Student.objects.create(
            user=user,
            college=application.college,
            department=application.department,
            branch=application.branch,
            academic_year=academic_year,
            enrollment_number=enrollment_number,
            roll_number=enrollment_number[-8:],
            semester=1,
            section='A',
            batch_year=timezone.localdate().year,
            date_of_birth=application.date_of_birth,
            gender=application.gender,
            address='Campus address pending',
            city='City',
            state='State',
            pincode='000000',
            emergency_contact=application.phone,
            emergency_contact_name='Guardian',
            admission_date=timezone.localdate(),
            admission_number=application.application_number,
        )

        application.status = 'ENROLLED'
        application.reviewed_by = enrolled_by
        application.reviewed_at = timezone.now()
        application.save(update_fields=['status', 'reviewed_by', 'reviewed_at'])

        return student
