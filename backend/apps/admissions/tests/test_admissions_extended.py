import datetime

import pytest
from rest_framework import status

from apps.admissions.models import AdmissionApplication, AdmissionCycle, AdmissionInquiry, MeritList


@pytest.mark.django_db
def test_list_applications(api_client, admin_user, department, branch):
    AdmissionApplication.objects.create(
        college=admin_user.college,
        application_number='APP-LIST-1',
        first_name='A',
        last_name='B',
        email='list@test.com',
        phone='+911111111111',
        date_of_birth=datetime.date(2005, 1, 1),
        gender='MALE',
        department=department,
        branch=branch,
        previous_school='X',
        previous_percentage=80,
        status='SUBMITTED',
    )
    api_client.force_authenticate(user=admin_user)
    r = api_client.get('/api/v1/admissions/')
    assert r.status_code == status.HTTP_200_OK
    assert len(r.data['data']) >= 1


@pytest.mark.django_db
def test_filter_by_status(api_client, admin_user, department, branch):
    api_client.force_authenticate(user=admin_user)
    r = api_client.get('/api/v1/admissions/', {'status': 'SUBMITTED'})
    assert r.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_application_detail(api_client, admin_user, department, branch):
    app = AdmissionApplication.objects.create(
        college=admin_user.college,
        application_number='APP-DET-1',
        first_name='Det',
        last_name='ail',
        email='det@test.com',
        phone='+912222222222',
        date_of_birth=datetime.date(2005, 1, 1),
        gender='MALE',
        department=department,
        branch=branch,
        previous_school='X',
        previous_percentage=80,
    )
    api_client.force_authenticate(user=admin_user)
    r = api_client.get(f'/api/v1/admissions/{app.id}/')
    assert r.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_patch_application_status(api_client, admin_user, department, branch):
    app = AdmissionApplication.objects.create(
        college=admin_user.college,
        application_number='APP-PATCH-1',
        first_name='P',
        last_name='atch',
        email='patch@test.com',
        phone='+913333333333',
        date_of_birth=datetime.date(2005, 1, 1),
        gender='MALE',
        department=department,
        branch=branch,
        previous_school='X',
        previous_percentage=80,
        status='SUBMITTED',
    )
    api_client.force_authenticate(user=admin_user)
    r = api_client.patch(
        f'/api/v1/admissions/{app.id}/',
        {'status': 'UNDER_REVIEW'},
        format='json',
    )
    assert r.status_code == status.HTTP_200_OK
    app.refresh_from_db()
    assert app.status == 'UNDER_REVIEW'


@pytest.mark.django_db
def test_kanban_board(api_client, admin_user, department, branch):
    for i, st in enumerate(['SUBMITTED', 'UNDER_REVIEW', 'ACCEPTED']):
        AdmissionApplication.objects.create(
            college=admin_user.college,
            application_number=f'APP-K{i}',
            first_name='K',
            last_name=str(i),
            email=f'kanban{i}@test.com',
            phone=f'+91444444444{i}',
            date_of_birth=datetime.date(2005, 1, 1),
            gender='MALE',
            department=department,
            branch=branch,
            previous_school='X',
            previous_percentage=80,
            status=st,
        )
    api_client.force_authenticate(user=admin_user)
    r = api_client.get('/api/v1/admissions/kanban/')
    assert r.status_code == status.HTTP_200_OK
    assert len(r.data['data']['SUBMITTED']) >= 1


@pytest.mark.django_db
@pytest.mark.parametrize(
    'status',
    ['DRAFT', 'SUBMITTED', 'UNDER_REVIEW', 'SHORTLISTED', 'REJECTED', 'ACCEPTED'],
)
def test_status_values_in_kanban(api_client, admin_user, department, branch, status):
    AdmissionApplication.objects.create(
        college=admin_user.college,
        application_number=f'APP-ST-{status}',
        first_name='S',
        last_name='T',
        email=f'{status.lower()}@test.com',
        phone='+915555555555',
        date_of_birth=datetime.date(2005, 1, 1),
        gender='MALE',
        department=department,
        branch=branch,
        previous_school='X',
        previous_percentage=80,
        status=status,
    )
    api_client.force_authenticate(user=admin_user)
    r = api_client.get('/api/v1/admissions/kanban/')
    assert status in r.data['data']


@pytest.mark.django_db
def test_list_inquiries(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    r = api_client.get('/api/v1/admissions/inquiries/')
    assert r.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_list_cycles(api_client, admin_user, academic_year):
    AdmissionCycle.objects.create(
        college=admin_user.college,
        name='Cycle A',
        academic_year=academic_year,
        start_date=datetime.date(2025, 1, 1),
        end_date=datetime.date(2025, 12, 31),
    )
    api_client.force_authenticate(user=admin_user)
    r = api_client.get('/api/v1/admissions/cycles/')
    assert r.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_merit_lists_empty(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    r = api_client.get('/api/v1/admissions/merit-lists/')
    assert r.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_student_cannot_list_admissions(api_client, college):
    from apps.accounts.models import User

    user = User.objects.create_user(
        email='nostu@college.edu',
        phone='+916666666666',
        first_name='No',
        last_name='Access',
        role='STUDENT',
        password='password',
        college=college,
    )
    api_client.force_authenticate(user=user)
    r = api_client.get('/api/v1/admissions/')
    assert r.status_code == status.HTTP_403_FORBIDDEN
