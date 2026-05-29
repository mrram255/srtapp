import datetime

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.colleges.models import AcademicYear, Branch, College, Department
from apps.notifications.models import Notification, NotificationPreference, UserNotification
from apps.students.models import Student


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def college(db):
    return College.objects.create(
        name='Notify College',
        code='NC01',
        address='Campus',
        city='City',
        state='State',
        pincode='123456',
        phone='+911111111111',
        email='notify@college.edu',
        established_year=2000,
        is_active=True,
    )


@pytest.fixture
def department(college):
    return Department.objects.create(college=college, name='CSE', code='CSE', is_active=True)


@pytest.fixture
def branch(college, department):
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
def academic_year(college):
    return AcademicYear.objects.create(
        college=college,
        year='2025-2026',
        start_date=datetime.date(2025, 6, 1),
        end_date=datetime.date(2026, 5, 31),
        is_current=True,
        is_active=True,
    )


@pytest.fixture
def admin_user(college):
    return User.objects.create_user(
        email='admin@notify.edu',
        phone='+912222222222',
        first_name='Admin',
        last_name='User',
        role='ADMIN',
        password='password',
        college=college,
    )


@pytest.fixture
def student_user(college, department, branch, academic_year):
    user = User.objects.create_user(
        email='student@notify.edu',
        phone='+913333333333',
        first_name='Stu',
        last_name='Dent',
        role='STUDENT',
        password='password',
        college=college,
    )
    Student.objects.create(
        user=user,
        college=college,
        department=department,
        branch=branch,
        academic_year=academic_year,
        enrollment_number='ENR001',
        roll_number='R001',
        semester=1,
        section='A',
        batch_year=2025,
        date_of_birth=datetime.date(2005, 1, 1),
        gender='MALE',
        address='Addr',
        city='City',
        state='State',
        pincode='111111',
        emergency_contact='+914444444444',
        emergency_contact_name='Parent',
        admission_date=datetime.date(2023, 7, 1),
        admission_number='ADM001',
    )
    return user


@pytest.fixture
def broadcast_notification(college, admin_user, student_user):
    notification = Notification.objects.create(
        college=college,
        title='Welcome',
        message='Hello campus',
        notification_type='GENERAL',
        category='general',
        recipients='ALL',
        sent_by=admin_user,
        send_push=True,
    )
    UserNotification.objects.create(
        user=student_user,
        notification=notification,
        college=college,
        is_delivered=True,
    )
    return notification
