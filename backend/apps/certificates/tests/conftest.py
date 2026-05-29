import datetime

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.fixture
def college(db):
    from apps.colleges.models import College

    return College.objects.create(
        name='Test College',
        code='TC001',
        address='123 Main St',
        city='Test City',
        state='Test State',
        country='India',
        pincode='123456',
        phone='+911234567890',
        email='info@testcollege.edu',
        established_year=2000,
        is_active=True,
    )


@pytest.fixture
def department(db, college):
    from apps.colleges.models import Department

    return Department.objects.create(college=college, name='Computer Science', code='CS', is_active=True)


@pytest.fixture
def branch(db, college, department):
    from apps.colleges.models import Branch

    return Branch.objects.create(
        college=college,
        department=department,
        name='CSE',
        code='CSE',
        duration_years=4,
        total_semesters=8,
        is_active=True,
    )


@pytest.fixture
def academic_year(db, college):
    from apps.colleges.models import AcademicYear

    return AcademicYear.objects.create(
        college=college,
        year='2025-2026',
        start_date=datetime.date(2025, 6, 1),
        end_date=datetime.date(2026, 5, 31),
        is_current=True,
        is_active=True,
    )


@pytest.fixture
def template_file():
    return SimpleUploadedFile('template.pdf', b'pdf-content', content_type='application/pdf')


@pytest.fixture
def super_admin_user(db, college):
    from apps.accounts.models import User

    return User.objects.create_superuser(
        email='admin@test.com',
        phone='+911111111111',
        first_name='Super',
        last_name='Admin',
        password='password',
        college=college,
    )


@pytest.fixture
def registrar_user(db, college):
    from apps.accounts.models import User

    return User.objects.create_user(
        email='registrar@test.com',
        phone='+944444444444',
        first_name='Reg',
        last_name='istrar',
        role='REGISTRAR',
        password='password',
        college=college,
    )


@pytest.fixture
def student_record(db, college, department, branch, academic_year):
    from apps.accounts.models import User
    from apps.students.models import Student

    user = User.objects.create_user(
        email='student@test.com',
        phone='+922222222222',
        first_name='Test',
        last_name='Student',
        role='STUDENT',
        password='password',
        college=college,
    )
    return Student.objects.create(
        user=user,
        college=college,
        department=department,
        branch=branch,
        academic_year=academic_year,
        enrollment_number='STU001',
        roll_number='R001',
        semester=1,
        section='A',
        batch_year=2025,
        date_of_birth=datetime.date(2005, 1, 1),
        gender='MALE',
        address='456 Student Lane',
        city='Student City',
        state='Student State',
        pincode='654321',
        emergency_contact='+933333333333',
        emergency_contact_name='Parent Name',
        admission_date=datetime.date(2023, 7, 1),
        admission_number='ADM001',
    )


@pytest.fixture
def certificate_template(db, college, template_file):
    from apps.certificates.models import CertificateTemplate

    return CertificateTemplate.objects.create(
        college=college,
        name='Bonafide',
        code='BONAFIDE-001',
        certificate_type='bonafide',
        template_file=template_file,
        is_active=True,
    )


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()
