from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.users.models import Role

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def super_admin_user(db):
    role = Role.objects.filter(name='super_admin').first()
    user = User.objects.create_user(
        email='audit-admin@example.com',
        phone='+919922233344',
        first_name='Audit',
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
