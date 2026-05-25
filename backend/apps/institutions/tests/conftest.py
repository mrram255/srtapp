from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.colleges.models import College, Department
from apps.users.models import Role

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def college(db):
    return College.objects.create(
        name='SRT College',
        code='SRT',
        address='Main Campus',
        city='Dhmari',
        state='Maharashtra',
        pincode='413801',
        phone='+919999999999',
        email='college@srtapp.com',
        established_year=1990,
    )


@pytest.fixture
def department(college):
    return Department.objects.create(
        college=college,
        name='Computer Science',
        code='CSE',
    )


@pytest.fixture
def super_admin_user(db):
    role = Role.objects.filter(name='super_admin').first()
    user = User.objects.create_user(
        email='s4admin@example.com',
        phone='+919911111111',
        first_name='Super',
        last_name='Admin',
        role='SUPER_ADMIN',
        role_ref=role,
        password='ValidPass1!',
    )
    user.set_password('ValidPass1!')
    user.save()
    return user


def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client
