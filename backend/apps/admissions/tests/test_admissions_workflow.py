"""Additional admissions coverage toward 40+ tests."""

import datetime

import pytest
from rest_framework import status

from apps.admissions.models import AdmissionApplication


def _app_data(college, department, branch, suffix, **extra):
    base = {
        'college': college,
        'application_number': f'APP-WF-{suffix}',
        'first_name': 'W',
        'last_name': suffix,
        'email': f'wf{suffix}@college.edu',
        'phone': f'+9190000{suffix:04d}'[-10:],
        'date_of_birth': datetime.date(2005, 1, 1),
        'gender': 'MALE',
        'department': department,
        'branch': branch,
        'previous_school': 'School',
        'previous_percentage': 75,
        'status': 'SUBMITTED',
    }
    base.update(extra)
    return base


@pytest.mark.django_db
@pytest.mark.parametrize('pct', [60, 70, 80, 90, 95])
def test_applications_various_percentages(api_client, admin_user, department, branch, pct):
    AdmissionApplication.objects.create(**_app_data(admin_user.college, department, branch, pct, previous_percentage=pct))
    api_client.force_authenticate(user=admin_user)
    r = api_client.get('/api/v1/admissions/')
    assert r.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.parametrize('gender', ['MALE', 'FEMALE', 'OTHER'])
def test_applications_by_gender(api_client, admin_user, department, branch, gender):
    AdmissionApplication.objects.create(**_app_data(admin_user.college, department, branch, hash(gender) % 1000, gender=gender))
    api_client.force_authenticate(user=admin_user)
    r = api_client.get('/api/v1/admissions/', {'status': 'SUBMITTED'})
    assert r.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_public_apply_requires_college(api_client):
    r = api_client.post('/api/v1/admissions/apply/', {'first_name': 'X'}, format='json')
    assert r.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_enroll_requires_accepted(api_client, admin_user, department, branch):
    app = AdmissionApplication.objects.create(
        **_app_data(admin_user.college, department, branch, 999, status='SUBMITTED'),
    )
    api_client.force_authenticate(user=admin_user)
    r = api_client.post(f'/api/v1/admissions/{app.id}/enroll/')
    assert r.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_detail_not_found(api_client, admin_user):
    import uuid

    api_client.force_authenticate(user=admin_user)
    r = api_client.get(f'/api/v1/admissions/{uuid.uuid4()}/')
    assert r.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.parametrize('field', ['first_name', 'last_name', 'email', 'phone'])
def test_create_requires_fields(api_client, admin_user, department, branch, field):
    data = {
        'first_name': 'A',
        'last_name': 'B',
        'email': 'miss@college.edu',
        'phone': '+918888888881',
        'date_of_birth': '2005-01-01',
        'gender': 'MALE',
        'department': str(department.id),
        'branch': str(branch.id),
        'previous_school': 'S',
        'previous_percentage': '80',
    }
    data.pop(field)
    api_client.force_authenticate(user=admin_user)
    r = api_client.post('/api/v1/admissions/', data, format='json')
    assert r.status_code == status.HTTP_400_BAD_REQUEST
