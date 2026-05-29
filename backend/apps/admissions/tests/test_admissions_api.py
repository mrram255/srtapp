import datetime

import pytest
from rest_framework import status

from apps.admissions.models import AdmissionApplication, AdmissionCycle, AdmissionInquiry
from apps.students.models import Student


@pytest.mark.django_db
def test_create_application(api_client, admin_user, department, branch):
    api_client.force_authenticate(user=admin_user)
    r = api_client.post(
        '/api/v1/admissions/',
        {
            'first_name': 'Ali',
            'last_name': 'Khan',
            'email': 'ali@apply.com',
            'phone': '+919999999999',
            'date_of_birth': '2005-01-01',
            'gender': 'MALE',
            'department': str(department.id),
            'branch': str(branch.id),
            'previous_school': 'High School',
            'previous_percentage': '85.5',
            'status': 'SUBMITTED',
        },
        format='json',
    )
    assert r.status_code == status.HTTP_201_CREATED
    assert r.data['data']['application_number']


@pytest.mark.django_db
def test_public_apply(api_client, college, department, branch):
    r = api_client.post(
        '/api/v1/admissions/apply/',
        {
            'college': str(college.id),
            'first_name': 'Pub',
            'last_name': 'Lic',
            'email': 'pub@apply.com',
            'phone': '+918888888888',
            'date_of_birth': '2005-06-15',
            'gender': 'FEMALE',
            'department': str(department.id),
            'branch': str(branch.id),
            'previous_school': 'School',
            'previous_percentage': '90',
        },
        format='json',
    )
    assert r.status_code == status.HTTP_201_CREATED
    assert 'application_number' in r.data['data']


@pytest.mark.django_db
def test_enroll_application(api_client, admin_user, department, branch, academic_year):
    app = AdmissionApplication.objects.create(
        college=admin_user.college,
        application_number='APP-TEST001',
        first_name='En',
        last_name='Roll',
        email='enroll@test.com',
        phone='+917777777777',
        date_of_birth=datetime.date(2005, 1, 1),
        gender='MALE',
        department=department,
        branch=branch,
        previous_school='X',
        previous_percentage=80,
        status='ACCEPTED',
    )
    api_client.force_authenticate(user=admin_user)
    r = api_client.post(f'/api/v1/admissions/{app.id}/enroll/')
    assert r.status_code == status.HTTP_200_OK
    assert Student.objects.filter(user__email='enroll@test.com').exists()
    app.refresh_from_db()
    assert app.status == 'ENROLLED'


@pytest.mark.django_db
def test_admission_cycle(api_client, admin_user, academic_year):
    api_client.force_authenticate(user=admin_user)
    r = api_client.post(
        '/api/v1/admissions/cycles/',
        {
            'name': '2025 intake',
            'academic_year': str(academic_year.id),
            'start_date': '2025-01-01',
            'end_date': '2025-08-31',
        },
        format='json',
    )
    assert r.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_admission_inquiry(api_client, admin_user, department):
    api_client.force_authenticate(user=admin_user)
    r = api_client.post(
        '/api/v1/admissions/inquiries/',
        {'name': 'Prospect', 'phone': '+916666666666', 'department': str(department.id)},
        format='json',
    )
    assert r.status_code == status.HTTP_201_CREATED
    assert AdmissionInquiry.objects.filter(name='Prospect').exists()
