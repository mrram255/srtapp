from __future__ import annotations

import pytest
from rest_framework.test import APIRequestFactory

from apps.accounts.models import User
from apps.core.permissions import (
    HasFieldPermission,
    HasModulePermission,
    IsAccountant,
    IsAdmissionStaff,
    IsHOD,
    IsOwnerOrAdmin,
    IsParent,
    IsPrincipal,
    IsRegistrar,
    IsStudent,
    IsSuperAdmin,
    IsTeacher,
)


@pytest.fixture
def factory():
    return APIRequestFactory()


def _make_user(role: str, **kwargs):
    defaults = {
        'email': f'{role.lower()}@example.com',
        'phone': f'+9199{abs(hash(role)) % 10_000_000:07d}',
        'first_name': 'Test',
        'last_name': role.title(),
        'role': role,
        'password': 'ValidPass2025!ab',
    }
    defaults.update(kwargs)
    return User.objects.create_user(**defaults)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'permission_cls,role,expected',
    [
        (IsSuperAdmin, 'SUPER_ADMIN', True),
        (IsSuperAdmin, 'STUDENT', False),
        (IsPrincipal, 'PRINCIPAL', True),
        (IsRegistrar, 'REGISTRAR', True),
        (IsAccountant, 'ACCOUNTANT', True),
        (IsAdmissionStaff, 'ADMISSION_OFFICER', True),
        (IsHOD, 'HOD', True),
        (IsTeacher, 'TEACHER', True),
        (IsStudent, 'STUDENT', True),
        (IsParent, 'PARENT', True),
    ],
)
def test_role_permissions(factory, permission_cls, role, expected):
    user = _make_user(role)
    request = factory.get('/')
    request.user = user
    assert permission_cls().has_permission(request, view=object()) is expected


@pytest.mark.django_db
def test_is_owner_or_admin_allows_owner(factory):
    owner = _make_user('STUDENT', email='owner@example.com', phone='+919900000001')

    class Obj:
        user = owner

    request = factory.get('/')
    request.user = owner
    assert IsOwnerOrAdmin().has_object_permission(request, view=object(), obj=Obj()) is True


@pytest.mark.django_db
def test_has_module_permission_with_user_checker(factory):
    user = _make_user('REGISTRAR')

    def checker(module, action):
        return module == 'students' and action == 'view'

    user.has_module_permission = checker  # type: ignore[attr-defined]

    class View:
        required_module = 'students'
        required_action = 'view'

    request = factory.get('/')
    request.user = user
    assert HasModulePermission().has_permission(request, View()) is True


@pytest.mark.django_db
def test_has_field_permission_blocks_restricted_field(factory):
    user = _make_user('TEACHER')

    def checker(module, field, action):
        return field != 'salary'

    user.has_field_permission = checker  # type: ignore[attr-defined]

    class View:
        required_module = 'staff'
        restricted_fields = ['salary']

    request = factory.patch('/', {'salary': '1000'}, format='json')
    request.user = user
    assert HasFieldPermission().has_permission(request, View()) is False
