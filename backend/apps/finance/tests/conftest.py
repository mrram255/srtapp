import datetime

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.colleges.models import AcademicYear, Branch, College, Department
from apps.finance.models import FeeStructure
from apps.students.models import Student


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def college(db):
    return College.objects.create(
        name='Fin College',
        code='FC01',
        address='A',
        city='C',
        state='S',
        pincode='111111',
        phone='+911111111111',
        email='fin@college.edu',
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
def accountant_user(college):
    return User.objects.create_user(
        email='acc@fin.edu',
        phone='+912222222222',
        first_name='Acc',
        last_name='User',
        role='ACCOUNTANT',
        password='password',
        college=college,
    )


@pytest.fixture
def student_record(college, department, branch, academic_year):
    user = User.objects.create_user(
        email='stu@fin.edu',
        phone='+933333333333',
        first_name='Stu',
        last_name='Fin',
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
        enrollment_number='FIN001',
        roll_number='R001',
        semester=1,
        section='A',
        batch_year=2025,
        date_of_birth=datetime.date(2005, 1, 1),
        gender='MALE',
        address='A',
        city='C',
        state='S',
        pincode='111111',
        emergency_contact='+944444444444',
        emergency_contact_name='P',
        admission_date=datetime.date(2023, 7, 1),
        admission_number='ADM001',
    )


@pytest.fixture
def fee_structure(college, department, academic_year):
    return FeeStructure.objects.create(
        college=college,
        name='Sem 1',
        department=department,
        semester=1,
        academic_year=academic_year,
        tuition_fee=50000,
        exam_fee=2000,
    )
