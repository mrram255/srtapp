import datetime

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.colleges.models import AcademicYear, College, Department


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def college(db):
    return College.objects.create(
        name='Dash College',
        code='DC01',
        address='Campus',
        city='City',
        state='State',
        pincode='123456',
        phone='+911111111111',
        email='dash@college.edu',
        established_year=2000,
    )


@pytest.fixture
def department(college):
    return Department.objects.create(college=college, name='CSE', code='CSE')


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
        email='admin@dash.edu',
        phone='+912222222222',
        first_name='Admin',
        last_name='User',
        role='ADMIN',
        password='password',
        college=college,
    )


@pytest.fixture
def principal_user(college):
    return User.objects.create_user(
        email='principal@dash.edu',
        phone='+913333333333',
        first_name='Principal',
        last_name='User',
        role='PRINCIPAL',
        password='password',
        college=college,
    )
