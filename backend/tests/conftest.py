"""Shared fixtures for top-level integration tests."""

import datetime

import pytest
from rest_framework.test import APIClient

from apps.colleges.models import AcademicYear, Branch, College, Department


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def college(db):
    return College.objects.create(
        name='Integration College',
        code='INT01',
        address='Campus',
        city='City',
        state='State',
        pincode='123456',
        phone='+911111111111',
        email='integration@college.edu',
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
