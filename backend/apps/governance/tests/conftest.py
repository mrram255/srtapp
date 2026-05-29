import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.colleges.models import College


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def college(db):
    return College.objects.create(
        name='Gov College',
        code='GC01',
        address='A',
        city='C',
        state='S',
        pincode='111111',
        phone='+911111111111',
        email='gov@college.edu',
        established_year=2000,
    )


@pytest.fixture
def principal_user(college):
    return User.objects.create_user(
        email='principal@gov.edu',
        phone='+912222222222',
        first_name='P',
        last_name='R',
        role='PRINCIPAL',
        password='password',
        college=college,
    )


@pytest.fixture
def admin_user(college):
    return User.objects.create_user(
        email='admin@gov.edu',
        phone='+913333333333',
        first_name='Admin',
        last_name='Gov',
        role='ADMIN',
        password='password',
        college=college,
    )
