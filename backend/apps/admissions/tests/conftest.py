import datetime

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.colleges.models import AcademicYear, Branch, College, Department


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def college(db):
    return College.objects.create(
        name='Adm College',
        code='AC01',
        address='A',
        city='C',
        state='S',
        pincode='111111',
        phone='+911111111111',
        email='adm@college.edu',
        established_year=2000,
    )


@pytest.fixture
def department(college):
    return Department.objects.create(college=college, name='CSE', code='CSE')


@pytest.fixture
def branch(college, department):
    return Branch.objects.create(
        college=college,
        department=department,
        name='CSE',
        code='CSE',
        duration_years=4,
        total_semesters=8,
    )


@pytest.fixture
def academic_year(college):
    return AcademicYear.objects.create(
        college=college,
        year='2025-2026',
        start_date=datetime.date(2025, 6, 1),
        end_date=datetime.date(2026, 5, 31),
        is_current=True,
    )


@pytest.fixture
def admin_user(college):
    return User.objects.create_user(
        email='admin@adm.edu',
        phone='+912222222222',
        first_name='Admin',
        last_name='Adm',
        role='ADMIN',
        password='password',
        college=college,
    )
